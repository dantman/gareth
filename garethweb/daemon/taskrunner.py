import time, logging, json
from garethweb.messagebroker import StompConnection
from garethweb.models import Remote

logging.basicConfig(level=logging.DEBUG)

class TaskListener(object):
	def on_error(self, headers, message):
		logging.error(message)

	def on_message(self, headers, message):
		logging.info(message)
		if headers.get('destination').startswith('/queue/task.remote.fetch'):
			cmd = json.loads(message)
			r = Remote.objects.get(name=cmd['name'])
			print "Running fetch for %s (%s)" % (r.name, r.project.name) 
			r.run_fetch()

class TaskRunner(object):
	def run(self):
		stomp = StompConnection()
		stomp.set_listener('task', TaskListener())
		stomp.start()
		stomp.connect(wait=True)
		stomp.subscribe(destination='/queue/task.remote.fetch', id='task-remote-fetch')

		try:
			while True:
				time.sleep(5)
		except KeyboardInterrupt:
			pass

		print "Quitting..."
		stomp.stop()

if __name__ == "__main__":
	TaskRunner().run()