from django.core.management.base import BaseCommand, CommandError
from garethweb.models import User, Role
from optparse import make_option

class Command(BaseCommand):
	args = '<username password>'
	option_list = BaseCommand.option_list + tuple( [
		make_option('-a', '--admin',
			dest="admin",
			action="store_true",
			default=False,
			help="Give the user the admin role.")
	] )
	help = 'Creates a user locally in the database.'

	def handle(self, *args, **options):
		if len(args) < 1:
			raise CommandError('Please specify a username')
		if len(args) < 2:
			raise CommandError('Please specify a password')

		user = User(username=args[0])
		user.set_password(args[1])
		user.save()

		if options['admin']:
			user.roles.add(Role.make('admin'))
			user.save()



		self.stdout.write("Created user '%s'\n" % user.username)