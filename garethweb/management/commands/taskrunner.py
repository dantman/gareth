import logging
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from garethweb.daemon.taskrunner import TaskRunner

class Command(BaseCommand):
	option_list = BaseCommand.option_list + tuple( [
		make_option('-d', '--debug',
			dest="debug",
			action="store_true",
			default=False,
			help="Enable verbose debug logging")
	] )
	help = 'Starts a taskrunner process'

	def handle(self, *args, **options):
		# @todo Support changing the logger options for loggers individually using the cli options
		if options.get('debug', False):
			logging.getLogger('taskrunner').setLevel(logging.DEBUG)
			logging.getLogger('stompest').setLevel(logging.DEBUG)
			logging.getLogger('procgit').setLevel(logging.DEBUG)
		# else:
			# logging.getLogger('taskrunner').setLevel(logging.INFO)

		TaskRunner().run()
