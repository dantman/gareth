from django.template.base import TemplateSyntaxError, Library, Node, token_kwargs
from django.template.defaultfilters import stringfilter
from django.utils.html import escape

register = Library()

@register.tag
def icon(parser, token):
	bits = token.split_contents()
	if len(bits) < 2:
		raise TemplateSyntaxError("'%s' requires at least one argument." % bits[0])
	name = parser.compile_filter(bits[1])
	remaining_bits = bits[2:]
	extra_context = token_kwargs(remaining_bits, parser)
	if remaining_bits:
		raise TemplateSyntaxError("%r received an invalid token: %r" % (bits[0], remaining_bits[0]))
	return IconNode(name=name, extra_context=extra_context)

class IconNode(Node):
	def __init__(self, name, extra_context):
		self.name = name
		self.extra_context = extra_context

	def __repr__(self):
		return "<IconNode>"

	def extra(self, key, context):
		extra = self.extra_context.get(key, None)
		if extra:
			return extra.resolve(context)
		return ''

	def render(self, context):
		icon = self.name.resolve(context)
		if not icon:
			return ''
		classname = 'icon-%s' % icon
		if self.extra('color', context):
			classname += ' icon-%s' % self.extra('color', context)
		before = self.extra('before', context)
		after = self.extra('after', context)
		return '%s<i class="%s"></i>%s' % (escape(before), escape(classname), escape(after))

@register.filter
@stringfilter
def btnclass(name):
	if name == 'fetch':
		return 'btn btn-inverse'
	if name == 'delete':
		return 'btn btn-danger'
	return 'btn'

@register.filter
@stringfilter
def maptoicon(name, arg=None):
	if arg == "crumbs":
		crumbs = True
	elif arg == None:
		crumbs = False
	else:
		raise TemplateSyntaxError("Unknown argument '%s' to maptoicon" % arg)
	if crumbs and name in ('projects', 'remotes', 'commits', 'users'):
		return 'list'
	if name == 'delete':
		return 'trash'
	if name == 'fetch':
		return 'refresh'
	if name == 'home':
		return 'home'
	if name == 'settings':
		return 'cog'
	if name in ('projects', 'project'):
		return 'leaf'
	if name in ('remotes', 'remote'):
		return 'download-alt'
	if name in ('commits', 'commit'):
		return 'barcode'
	if name in ('users', 'user', 'profile', 'login'):
		return 'user'
	if name == 'logout':
		return 'off'
	if name == 'identities':
		return 'envelope'
	if name == 'create':
		return 'plus'
	if name == 'settings':
		return 'cog'
	return ''
