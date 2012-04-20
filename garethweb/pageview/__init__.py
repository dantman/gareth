from django.http import HttpResponse
from django.template import RequestContext
from django.utils.html import escape
from django.core.urlresolvers import reverse, reverse_lazy
from garethweb.pageview.template import get_template
from garethweb.models import Project, Remote, User

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
		if crumb not in self._crumbs:
			self._crumbs.append(crumb)

# Navigation list
_navigation = []
def navigation(name, order=10):
	def _(f):
		_navigation.append({
			'href': reverse_lazy("%s.%s" % (f.__module__, f.__name__)),
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
		self.theme = 'bootstrap'

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
		navigation = list(_navigation)
		navigation.sort(key=lambda n: n['order'])
		return navigation

	@property
	def tabs(self):
		return None

	@property
	def template(self):
		return get_template(self.theme, ('view',)+self.page)
		# return get_template(':'.join(('view',)+self.page))

	@property
	def context(self):
		d = self.dict.copy()
		d['page_title'] = self.title_text
		d['title'] = self.title_html
		d['breadcrumbs'] = self.breadcrumbs
		d['navigation'] = self.navigation
		d['tabs'] = self.tabs
		return RequestContext(self.request, d)

	@property
	def response(self):
		return HttpResponse(self.template.render(self.context))

	def __call__(self):
		return self.response
