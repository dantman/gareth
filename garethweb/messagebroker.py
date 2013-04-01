import threading, logging, stomp
from gareth.settings import STOMP

# @todo This is typically overridden by gevent and will likely result in each greenlet
#       (ie: each request) having it's own connection. Our real goal is simply to avoid
#       different threads from trying to use the same STOMP connection at the exact same time.
#       In theory it should be perfectly fine for greenlets on the same thread to use the same STOMP connection.
#       Consider tweaking this so it is in fact a real threading local instead of a greenlet local.
_local_thread = threading.local()

class BasicListener(object):
	def on_error(self, headers, message):
		logging.error(message)

	def on_message(self, headers, message):
		# Don't do anything
		pass

def StompConnection():
	return stomp.Connection(
		STOMP['hosts'],
		user=STOMP.get('user', None),
		passcode=STOMP.get('pass', None),
		use_ssl=STOMP.get('ssl', False),
		version=STOMP.get('version', 1.0)
	)

def get_local_stomp():
	if not getattr(_local_thread, 'stomp_connection', None):
		conn = StompConnection()
		conn.set_listener('basic', BasicListener())
		conn.start()
		conn.connect()
		_local_thread.stomp_connection = conn
	
	return _local_thread.stomp_connection

def send(*args, **kwargs):
	get_local_stomp().send(*args, **kwargs)
