from django.template.base import TemplateSyntaxError, Library
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re

register = Library()

@register.filter(needs_autoescape=True)
@stringfilter
def commitmessage(message, autoescape=None):
	if autoescape:
		message = conditional_escape(message)
	message = re.sub("(\r\n|\r|\n)", "<br>\n", message)
	return mark_safe(message)
