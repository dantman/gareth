from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import django.contrib.auth.hashers as pw
from collections import defaultdict
from garethgit import GarethGit
import gareth.settings as settings

class Project(models.Model):
	"""
	Gareth project. Essentially what wraps around a git repository.
	"""
	name = models.CharField(max_length=255, unique=True)
	description = models.TextField(blank=True)

	def _get_git_path(self):
		return "%s/%s" % (settings.REPO_PATH, self.name)

	git_path = property(_get_git_path)

	def _get_git(self):
		return GarethGit(self.git_path)

	git = property(_get_git)

	def __unicode__(self):
		return self.name

class Role(models.Model):
	"""
	Gareth user role for the permissions model.
	"""
	role = models.CharField(max_length=20, unique=True)
	name = models.CharField(max_length=100)

	@staticmethod
	def make(role, name=None):
		try:
			return Role.objects.get(role=role)
		except ObjectDoesNotExist:
			pass
		if name is None:
			name = role
		return Role(role=role, name=name)

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

	def _get_rights(self):
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
	rights = property(_get_rights)

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

class Remote(models.Model):
	"""
	Remotes. Provides user-specific git remotes for fetching from.
	"""
	project = models.ForeignKey(Project)
	user = models.ForeignKey(User)
	name = models.CharField(max_length=40, unique=True)
	url = models.CharField(max_length=255)

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.url)
