import logging, gevent
from garethweb.messagebroker import client as mb_client
from garethweb.models import Remote

logger = logging.getLogger('taskrunner')
logger.setLevel(logging.DEBUG)

class TaskRunner(object):
	def on_task_remote_fetch(self, cmd, frame):
		logging.debug(frame.body)
		r = Remote.objects.get(name=cmd['name'])
		logger.debug("Running fetch for %s (%s)" % (r.name, r.project.name))
		r.run_fetch()

	def run(self):
		# @fixme Reconnect handling both on startup and while processing
		logger.info("Task runner starting")
		stomp = mb_client()
		stomp.connect()
		logger.info("Connected")
		stomp.on('/queue/task.remote.fetch', self.on_task_remote_fetch)
		logger.debug("Subscribed to /queue/task.remote.fetch")

		stomp.join()

		logger.info("Quitting...")

if __name__ == "__main__":
	# gevent.signal(signal.SIGQUIT, gevent.shutdown)
	TaskRunner().run()
