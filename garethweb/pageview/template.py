from django.template.base import TemplateDoesNotExist
from django.template import loader
from django.template.loader import BaseLoader, find_template_loader, select_template
from django.conf import settings
from garethweb.pageview import utils

def get_template(theme, keys):
	return loader.get_template(':'.join(keys))

class Loader(BaseLoader):
	is_usable = True

	def __init__(self, loaders):
		self._loaders = loaders
		self._cached_loaders = []

	@property
	def loaders(self):
		# Resolve loaders on demand to avoid circular imports
		if not self._cached_loaders:
			cached_loaders = []
			for loader in self._loaders:
				cached_loaders.append(find_template_loader(loader))
			self._cached_loaders = cached_loaders
		return self._cached_loaders

	def find_template_source(self, template_name, template_dirs=None):
		for loader in self.loaders:
			try:
				return loader.load_template_source(template_name, template_dirs)
			except TemplateDoesNotExist:
				pass
		raise TemplateDoesNotExist(template_name)

	def load_template_source(self, template_name, template_dirs=None):
		# Only applies to things like view:project:show
		if ':' not in template_name or '/' in template_name:
			raise TemplateDoesNotExist(template_name)

		# Extract the current request from the thread
		request = utils.get_request()
		keys = '/'.join(template_name.split(':'))
		tpl_names = []
		# Use the theme from the request if we got ahold of the request
		if request and request.theme:
			tpl_names.append("themes/%s/%s.html" % (request.theme, keys))
		tpl_names.append("%s.html" % keys)
		for tpl_name in tpl_names:
			try:
				return self.find_template_source(tpl_name, template_dirs)
			except TemplateDoesNotExist:
				pass
		raise TemplateDoesNotExist(template_name)
