from pygments.formatters.html import HtmlFormatter
from django.http import HttpResponse
from django.views.decorators.gzip import gzip_page

@gzip_page
def pygments(request):
	body = HtmlFormatter().get_style_defs('.highlight')
	return HttpResponse(body, content_type='text/css')
