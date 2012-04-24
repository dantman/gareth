from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from garethweb.models import Remote

class Command(BaseCommand):
	args = '<remote_id>'
	help = 'Runs a fetch of a remote.'

	def handle(self, *args, **options):
		if len(args) < 1:
			raise CommandError('Please specify a remote id')

		def progress(state):
			if state.is_completed:
				if state.is_finished:
					msg = "Finished"
				else:
					msg = "Failed"
			else:
				msg = "Progress: %s%%" % state.progress
			self.stdout.write('%s\n' % msg)

		try:
			remote = Remote.objects.get(name=args[0])
			self.stdout.write("Fetching remote '%s' for user '%s' of project '%s'.\n" % (remote.name, remote.user.username, remote.project.name))
			remote.run_fetch(progress)
		except ObjectDoesNotExist:
			raise CommandError("No remote by the name '%s' exists.\n" % args[0])
