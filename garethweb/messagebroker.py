import threading, gevent, logging, json
from stompest.error import StompConnectTimeout, StompConnectionError
from stompest.config import StompConfig
from stompest.protocol import StompSpec, StompSession
from stompest.sync import Stomp
from gevent import monkey
from gareth.settings import STOMP

# Make certain that socket and select have been monkeypatched
monkey.patch_all(thread=False)

logger = logging.getLogger('messagebroker')
logger.setLevel(logging.DEBUG)

# @todo This is typically overridden by gevent and will likely result in each greenlet
#       (ie: each request) having it's own connection. Our real goal is simply to avoid
#       different threads from trying to use the same STOMP connection at the exact same time.
#       In theory it should be perfectly fine for greenlets on the same thread to use the same STOMP connection.
#       Consider tweaking this so it is in fact a real threading local instead of a greenlet local.
_local_thread = threading.local()

def _get_config():
	# Hosts
	hosts = STOMP.get('hosts', None)
	if not hosts:
		host = STOMP.get('host', None)
		if not host:
			host = ('localhost', 61613)
		if host:
			hosts = (host,)

	hostname = hosts[0]
	if isinstance(hostname, tuple):
		hostname = hostname[0]
	else:
		hostname = hostname.split(':')[0]

	# Uris
	uris = []
	for host in hosts:
		if isinstance(host, tuple):
			host = "%s:%d" % host
		uri = "tcp://%s" % host
		uris.append(uri)

	if len(hosts) > 1:
		# @todo Give config better control over fallover settings
		final_uri = "fallover:(%s)" % ','.join(uris)
	else:
		final_uri = uris[0]

	# User, passcode
	user = STOMP.get('user', None),
	if user == '':
		user = None

	passcode = STOMP.get('pass', None),
	if passcode == '':
		passcode = None

	CONFIG = StompConfig(
		uri=final_uri,
		login=user,
		passcode=passcode,
		# Support the latest version of the spec that existed when we wrote this
		# (and due to stompest's accepts-version header every version before that)
		version=StompSpec.VERSION_1_2
	)
	EXTRA = {
		'hostname': hostname,
	}
	return CONFIG, EXTRA

class Subscription(object):
	def __init__(self, conn, destination, token, callback):
		self.conn = conn
		self.token = token
		self.destination = destination
		self.callback = callback

	def call(self, frame):
		content_type = frame.headers.get(StompSpec.CONTENT_TYPE_HEADER, '')
		if content_type == 'application/json;charset=UTF-8':
			return gevent.spawn(self.callback, json.loads(frame.body), frame)
		logger.error("Received frame for subscription %s (%s) but did not find acceptable content-type header: %s"
			% (self.destination, self.token, frame.info()))

	def unsubscribe(self):
		# @todo Include a receipt request and use it to unset the subscriptions key at the right time
		self.conn.stompest.unsubscribe(self.token)


class Client(object):
	def __init__(self):
		self.stompest = None
		self.greenlet = None
		self.subscriptions = {}
		self._last_id = 0

	def _next_id(self):
		self._last_id += 1
		return self._last_id

	def connect(self):
		if not self.stompest:
			CONFIG, EXTRA = _get_config()
			self._hostname = EXTRA.get('hostname', None)
			self.stompest = Stomp(CONFIG)

		if self.stompest.session.state != StompSession.DISCONNECTED:
			return

		while True:
			try:
				self.stompest.connect(host=self._hostname)
				logger.info('Connected')
				break
			except StompConnectTimeout:
				continue

		if not self.greenlet:
			self.greenlet = gevent.spawn(self._run)

	def _run(self):
		while True:
			try:
				frame = self.stompest.receiveFrame()
				self.stompest.ack(frame)
				if frame.command == 'ERROR':
					logger.error(frame.info())
				elif frame.command == 'MESSAGE':
					token = self.stompest.message(frame)
					if self.subscriptions.get(token):
						subscription = self.subscriptions[token]
						subscription.call(frame)
					else:
						logger.error("Received a message for %s (%s) but there was no matching subscription."
							% (frame.headers.get(StompSpec.DESTINATION_HEADER, '???'), token))
				else:
					logger.warning("Unknown frame: %s" % frame.info())
				# @todo Handle receipts
			except (gevent.GreenletExit, KeyboardInterrupt):
				# @todo Include a receipt in the disconnect. And instead of breaking right away wait for the
				#       receipt frame before disconnecting and consider waiting on any greenlets we started.
				self.stompest.disconnect()
				break
			except StompConnectionError:
				# We've been disconnected from the server. Try reconnecting to it.
				self.connect()

	def on(self, destination, callback):
		self.connect()
		token = self.stompest.subscribe(destination, {
			StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL,
			StompSpec.ID_HEADER: self._next_id(),
		})
		subscription = Subscription(
			conn=self,
			destination=destination,
			token=token,
			callback=callback
		)
		self.subscriptions[subscription.token] = subscription;

	# @todo consider adding optional support for additional custom headers
	def send(self, cmd, destination):
		self.connect()
		body = json.dumps(cmd)
		headers = {}
		headers[StompSpec.CONTENT_TYPE_HEADER] = 'application/json;charset=UTF-8'
		self.stompest.send(destination, body, headers)

	def join(self):
		try:
			self.connect()
		except (gevent.GreenletExit, KeyboardInterrupt):
			return
		try:
			gevent.joinall([self.greenlet])
		except KeyboardInterrupt:
			self.greenlet.kill(block=True)

def client():
	if not getattr(_local_thread, 'client', None):
		conn = Client()
		# conn.connect()
		_local_thread.client = conn
	
	return _local_thread.client

def send(*args, **kwargs):
	client().send(*args, **kwargs)

