from django.template.base import TemplateSyntaxError, Library, Node, token_kwargs
from django.template.defaultfilters import stringfilter
from django.utils.timesince import timesince

register = Library()

@register.filter
def timesince(datetime):
	return timesince(datetime)
