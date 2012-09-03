from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from garethweb.daemon.taskrunner import TaskRunner

class Command(BaseCommand):
	# args = '<username password>'
	option_list = BaseCommand.option_list + tuple( [
		# make_option('-a', '--admin',
		# 	dest="admin",
		# 	action="store_true",
		# 	default=False,
		# 	help="Give the user the admin role.")
	] )
	help = 'Starts a taskrunner process'

	def handle(self, *args, **options):
		TaskRunner().run()
