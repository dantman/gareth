from django.http import HttpResponse
from django.template import RequestContext
from django.utils.html import escape
from django.core.urlresolvers import reverse, reverse_lazy
from garethweb.pageview.template import get_template
from garethweb.models import Project, Remote, User
from garethgit import GarethGitCommit
import re

# Page breadcrumb handling
class Breadcrumbs():
	def __init__(self):
		self.home = False
		self._crumbs = []

	@property
	def crumbs(self):
		crumbs = []
		def add(name=None, text=None, href=None, active=False):
			d = { 'name': name, 'text': text }
			if isinstance(href, tuple):
				href = reverse(href[0], kwargs=href[1])
			d['href'] = href
			d['active'] = active
			crumbs.append(d)

		add(name='home', href=reverse('home'), text='Home')
		if not len(self._crumbs) and not self.home:
			add(name='other', text='???', active=True)

		for crumb in self._crumbs:
			if crumb == Project:
				add(name='projects', text='Projects', href=reverse('projects'))
			elif isinstance(crumb, Project):
				add(name='project', text=crumb.name, href=('project', {'name': crumb.name}))
			elif isinstance(crumb, Remote):
				add(name='remotes', text='Remotes', href=('project_remotes', {'project': crumb.project}))
				if crumb.name:
					add(name='remote', text='Remote', href=('remote', {'project': crumb.project, 'ID': crumb.name}))
				else:
					# Remote with no ID, this is likely a trick we use to add the project remotes
					# piece to the breadcrumbs
					pass
			elif crumb == User:
				add(name='users', text='Users', href=reverse('users'))
			elif isinstance(crumb, User):
				add(name='user', text=crumb.username, href=('user', {'username': crumb.username}))
			elif crumb == GarethGitCommit:
				add(name='commits', text='Commits')
			elif isinstance(crumb, GarethGitCommit):
				add(name='commit', text=crumb.sha1)
			elif type(crumb) == str:
				add(name=crumb.lower(), text=crumb)
			else:
				raise BaseException("Unknown crumb %s" % crumb)

		crumbs[-1]['href'] = None
		crumbs[-1]['active'] = True

		return crumbs

	def add(self, crumb):
		if crumb == 'home':
			self.home = True
			return
		elif isinstance(crumb, Project):
			self.add(Project)
		elif isinstance(crumb, Remote):
			self.add(crumb.project)
		elif isinstance(crumb, User):
			self.add(User)
		elif isinstance(crumb, GarethGitCommit):
			self.add(GarethGitCommit)
		if crumb not in self._crumbs:
			self._crumbs.append(crumb)

# Navigation list
_navigation = []
def navigation(name, order=10, key=None):
	def _(f):
		view = "%s.%s" % (f.__module__, f.__name__)
		thekey = key
		if not thekey:
			thekey = re.sub('^garethweb.views.', '', view)
		_navigation.append({
			'name': thekey,
			'href': reverse_lazy(view),
			'text': name,
			'order': order,
		})
		return f
	return _

# View class
class GarethView():
	def __init__(self, request, page):
		self.title = ()
		self.request = request
		self.page = page
		self.dict = {}
		self._breadcrumbs = Breadcrumbs()
		self.buttons = []
		self.theme = 'bootstrap'
		self.activenav = ()
		self.activetab = ()

	def set(self, *args, **kwargs):
		for k in kwargs:
			self.dict[k] = kwargs[k]

	def crumb(self, *crumbs):
		for crumb in crumbs:
			self._breadcrumbs.add(crumb)

	@property
	def title_text(self):
		title = []
		for x in self.title:
			if isinstance(x, tuple):
				title.append(x[1])
			else:
				title.append(x)
		if len(title) > 0:
			title.append('-')
		title.append('Gareth') # @fixme Sitename
		return ' '.join(title)

	@property
	def title_html(self):
		title = []
		for x in self.title:
			if isinstance(x, tuple):
				title.append(escape(x[1]))
			else:
				title.append(escape(x))
		return ' '.join(title)

	@property
	def breadcrumbs(self):
		return self._breadcrumbs.crumbs

	@property
	def navigation(self):
		navi = []
		for nav in _navigation:
			navi.append(nav.copy())
		navi.sort(key=lambda n: n['order'])
		return navi

	@property
	def personalbar(self):
		if self.request.currentuser:
			return [
				{ 'name': 'profile', 'active': ('user-%s' % self.request.currentuser.username), 'href': reverse('profile'), 'text': 'Profile' },
				{ 'name': 'settings', 'href': reverse('settings'), 'text': 'Settings' },
				{ 'name': 'logout', 'href': reverse('logout'), 'text': 'Logout' },
			]
		else:
			return [
				{ 'name': 'login', 'href': reverse('login'), 'text': 'Login' },
			]

	@property
	def tabs(self):
		return ()

	def add_button(self, href=None, post=False, text=None, name=None):
		b = {}
		if not name:
			name = text.lower()
		b['href'] = href
		b['text'] = text
		b['name'] = name
		if post:
			b['method'] = 'POST'
			if isinstance(post, dict):
				b['data'] = post
		self.buttons.append(b)

	@property
	def template(self):
		return get_template(self.theme, ('view',)+self.page)
		# return get_template(':'.join(('view',)+self.page))

	@property
	def context(self):
		def isactive(d, active):
			if type(active) == str:
				active = (active,)
			name = d.get('name', None)
			if d.get('active', None) == True:
				return True 
			if name in active:
				return True
			a = d.get('active', None)
			if a:
				return len([x for x in active if x in a]) > 0
			return False

		d = self.dict.copy()
		d['page_title'] = self.title_text
		d['title_html'] = self.title_html
		d['breadcrumbs'] = self.breadcrumbs
		d['navigation'] = self.navigation
		for nav in d['navigation']:
			nav['active'] = isactive(nav, self.activenav)
		d['personalbar'] = self.personalbar
		for bar in d['personalbar']:
			bar['active'] = isactive(bar, self.activenav)
		d['tabs'] = []
		for origtab in self.tabs:
			tab = origtab.copy()
			tab['active'] = isactive(tab, self.activetab)
			d['tabs'].append(tab)
		d['buttons'] = self.buttons
		return RequestContext(self.request, d)

	@property
	def response(self):
		return HttpResponse(self.template.render(self.context))

	def __call__(self):
		return self.response
