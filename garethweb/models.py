from collections import defaultdict
from django.utils.timezone import now
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import django.contrib.auth.hashers as pw
from garethgit import GarethGit
import gareth.settings as settings

class Project(models.Model):
	"""
	Gareth project. Essentially what wraps around a git repository.
	"""
	name = models.CharField(max_length=255, unique=True)
	description = models.TextField(blank=True)

	@property
	def git_path(self):
		return "%s/%s.git/" % (settings.REPO_PATH, self.name)

	@property
	def git(self):
		return GarethGit(self.git_path)

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('project', (), { 'name': self.name })

class Role(models.Model):
	"""
	Gareth user role for the permissions model.
	"""
	role = models.CharField(max_length=20, unique=True)

	@staticmethod
	def make(role, name=None):
		try:
			return Role.objects.get(role=role)
		except ObjectDoesNotExist:
			Role(role=role).save()
		return Role.objects.get(role=role)

	def __unicode__(self):
		return self.role

class User(models.Model):
	"""
	Gareth user model.
	Django's built-in model pre-defines to much we don't want so we have our own model written from scratch.
	"""
	username = models.CharField(max_length=255, unique=True)
	auth = models.CharField(max_length=255, unique=True)
	roles = models.ManyToManyField(Role)

	def __unicode__(self):
		return self.username

	@property
	def rights(self):
		rights = defaultdict(lambda: False)
		rights['user'] = True
		if 'user' in settings.ROLE_HIERARCHY:
			for hright in settings.ROLE_HIERARCHY['user']:
				rights[hright] = True
		for role in self.roles.all():
			right = role.role
			rights[right] = True
			if right in settings.ROLE_HIERARCHY:
				for hright in settings.ROLE_HIERARCHY[right]:
					rights[hright] = True
		return rights

	def compare_password(self, password):
		type, _, auth = self.auth.partition('$')
		if type == 'password':
			# @fixme Give check_password a setter so the password will be updated
			return pw.check_password(password, auth)
		else:
			raise Exception("Unknown auth type %s" % type)

	def set_password(self, password, force=False):
		type, _, auth = self.auth.partition('$')
		if type and type != 'password' and not force:
			raise Exception("Cannot overwrite ext auth with password auth")
		self.auth = 'password$%s' % pw.make_password(password)

	@models.permalink
	def get_absolute_url(self):
		return ('user', (), { 'username': self.username })

class UserEmail(models.Model):
	"""
	A user identity. Essentially a user's email address.
	We work with git so a user may have multiple addresses they want to have associated with them.
	"""
	user = models.ForeignKey(User)
	email = models.EmailField(max_length=255, unique=True)

	def __unicode__(self):
		return self.email

class UnconfirmedUserEmail(models.Model):
	"""
	An unconfirmed UserEmail.
	Stored in a separate table along with a confirmation token until the user confirms it.
	"""
	user = models.ForeignKey(User)
	email = models.EmailField(max_length=255)
	token = models.CharField(max_length=64, db_index=True)

	def __unicode__(self):
		return self.email

class RemoteFetch(models.Model):
	"""
	Represents the status and progress of the fetch action of a remote.
	"""
	started_at = models.DateTimeField(auto_now_add=True)
	completed_at = models.DateTimeField(null=True)
	status_choices = (
		(0, 'Running'),
		(1, 'Finished'),
		(2, 'Failed')
	)
	status = models.PositiveSmallIntegerField(default=0, choices=status_choices)
	compressing_objects = models.PositiveSmallIntegerField(default=0)
	receiving_objects = models.PositiveSmallIntegerField(default=0)
	resolving_deltas = models.PositiveSmallIntegerField(default=0)

	@property
	def status_label(self):
		for choice in self.status_choices:
			if self.status is choice[0]:
				return choice[1]
		return None

	@property
	def progress(self):
		progress = [0, 0, 0]
		if self.resolving_deltas > 0:
			progress[0] = 100
			progress[1] = 100
			progress[2] = self.resolving_deltas
		elif self.receiving_objects > 0:
			progress[0] = 100
			progress[1] = self.receiving_objects
		else:
			progress[0] = self.compressing_objects
		return sum(progress) / 3

	@property
	def is_completed(self):
		return self.status != 0

	@property
	def is_finished(self):
		return self.status == 1

	def __unicode__(self):
		return "%s (started: %s, completed: %s, progress: %s%%)" % (self.status_label, self.started_at, self.completed_at, self.progress)

class Remote(models.Model):
	"""
	Remotes. Provides user-specific git remotes for fetching from.
	"""
	project = models.ForeignKey(Project)
	user = models.ForeignKey(User)
	name = models.CharField(max_length=40, unique=True)
	url = models.CharField(max_length=255)
	fetchstate = models.OneToOneField(RemoteFetch, null=True)

	@property
	def branches(self):
		return self.project.git.remote_branches(self.name)

	def queue_fetch(self):
		pass

	def run_fetch(self, progress=None):
		state = RemoteFetch()
		state.save()
		if self.fetchstate:
			self.fetchstate.delete()
		self.fetchstate = state
		self.save()
		def handle_progress(event, p):
			if event == 'compressing-objects':
				state.compressing_objects = p
			elif event == 'receiving-objects':
				state.receiving_objects = p
			elif event == 'resolving-deltas':
				state.resolving_deltas = p
			state.save()
			if progress:
				progress(state)
		ret = self.project.git.fetch(self.name, progress=handle_progress)
		if ret:
			state.status = 1
		else:
			state.status = 2
		state.completed_at = now()
		state.save()
		progress(state)

	def delete(self, *args, **kwargs):
		self.project.git.rm_remote(self.name)
		super(Remote, self).delete(*args, **kwargs)

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.url)

	@models.permalink
	def get_absolute_url(self):
		return ('remote', (), { 'project': self.project.name, 'ID': self.name })
