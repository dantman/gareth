from django.template.base import Library
from django.template.defaultfilters import stringfilter
import re

register = Library()

@register.filter
@stringfilter
def split(string, by):
	return string.split(by)

@register.filter
@stringfilter
def splitre(string, by):
	return re.split(by, string)
