from django.conf import settings
from django.utils.functional import SimpleLazyObject
from garethweb.pageview import utils

def get_theme(request):
	if not hasattr(request, '_cached_theme'):
		request._cached_theme = getattr(settings, 'DEFAULT_THEME', None)

	return request._cached_theme

class ThemeMiddleware(object):
	def process_request(self, request):
		# Store the current request in the local thread so the template loader has access
		utils.set_request(request)

		request.theme = SimpleLazyObject(lambda: get_theme(request))
