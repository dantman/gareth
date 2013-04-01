import time, logging, json
from garethweb.messagebroker import StompConnection
from garethweb.models import Remote

logging.basicConfig(level=logging.DEBUG)

class TaskListener(object):
	def __init__(self, out):
		self.out = out

	def on_error(self, headers, message):
		logging.error(message)

	def on_message(self, headers, message):
		logging.info(message)
		if headers.get('destination').startswith('/queue/task.remote.fetch'):
			cmd = json.loads(message)
			r = Remote.objects.get(name=cmd['name'])
			self.out.write("Running fetch for %s (%s)\n" % (r.name, r.project.name))
			r.run_fetch()

class TaskRunner(object):
	def run(self, out):
		out.write("Task runner starting\n")
		stomp = StompConnection()
		stomp.set_listener('task', TaskListener(out))
		stomp.start()
		stomp.connect(wait=True)
		out.write("Connected\n")
		stomp.subscribe(destination='/queue/task.remote.fetch', id='task-remote-fetch')
		out.write("Subscribed to /queue/task.remote.fetch\n")

		try:
			while True:
				time.sleep(5)
		except KeyboardInterrupt:
			pass

		out.write("Quitting...\n")
		stomp.stop()

if __name__ == "__main__":
	import sys
	TaskRunner().run(sys.stdout)