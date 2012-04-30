from django.template.base import TemplateSyntaxError, Library, Variable, Node
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

@register.filter('map')
def do_map(list, var):
	try:
		iter(list)
	except TypeError:
		# Not iterable, return an empty array
		return []
	return map(lambda item: Variable(var).resolve(item), list)

@register.tag('join')
def do_join_tag(parser, token):
	bits = token.split_contents()
	options = { 'by': ', ' }
	tag = bits.pop(0)
	if len(bits) < 1:
		raise TemplateSyntaxError("'%s' requires at least one argument." % tags)
	options['var'] = parser.compile_filter(bits.pop(0))
	while len(bits) > 0:
		arg = bits.pop(0)
		if arg not in ('as', 'by'):
			raise TemplateSyntaxError("Unknown argument '%s' to tag '%s'." %  (arg, tags))
		if len(bits) < 1:
			raise TemplateSyntaxError("'%s's arg '%s' requires one argument value." %  (arg, tags))
		value = bits.pop(0)
		options[arg] = value

	if 'as' in options:
		nodelist = parser.parse(('endjoin',))
	else:
		nodelist = False

	parser.delete_first_token()

	return JoinNode(nodelist, options)

class JoinNode(Node):
	def __init__(self, nodelist, options):
		self.nodelist = nodelist
		self.options = options

	def __repr__(self):
		return "<JoinNode>"

	def render(self, context):
		output = []
		if 'as' in self.options:
			for item in self.options['var'].resolve(context):
				context.update({ self.options['as']: item })
				output.append(self.nodelist.render(context))
				context.pop()
		else:
			raise NotImplemented()
		return self.options['by'].join(output)
