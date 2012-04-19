from django.conf import settings
from django.template.base import TemplateSyntaxError, Library, Variable, Node, token_kwargs, VARIABLE_ATTRIBUTE_SEPARATOR

register = Library()

def token_parse(parser, token, asvar=False):
	bits = token.contents.split()
	options = {}
	tag = bits.pop(0)
	if len(bits) < 1:
		raise TemplateSyntaxError('%s requires at least a single argument' % tag)

	if asvar:
		options['var'] = Variable(bits.pop(0))
		if len(bits) > 0 and bits[0] == 'as':
			bits.pop(0)
			if bits[0].startswith('@'):
				options['type'] = bits.pop(0)[1:]
			options['as'] = bits.pop(0)
	else:
		if bits[0].startswith('@'):
			options['type'] = bits.pop(0)[1:]
		options['var'] = Variable(bits.pop(0))

	if len(bits) > 0:
		raise TemplateSyntaxError('Too many arguments to %s' % tag)

	return options

@register.tag
def withtable(parser, token):
	options = token_parse(parser, token)
	nodelist = parser.parse(('endwithtable',))
	parser.delete_first_token()

	return WithTableNode(nodelist, options)

class WithTableNode(Node):
	def __init__(self, nodelist, options):
		self.nodelist = nodelist
		self.options = options
		self.var = options['var']

	def __repr__(self):
		return "<WithTableNode>"

	def new_table(self):
		t = self.options.get('type', None)
		if t == 'kv':
			return []
		elif t == 'multibody':
			return {
				'headers': [],
				'bodies': [],
			}
		else:
			return {
				'headers': [],
				'rows': [],
			}

	def render(self, context):
		values = { self.var.var: self.new_table() }
		context.update(values)
		output = self.nodelist.render(context)
		context.pop()
		return output

@register.tag
def appendto(parser, token):
	options = token_parse(parser, token, asvar=True)
	nodelist = parser.parse(('endappendto',))
	parser.delete_first_token()

	return AppendToNode(nodelist, options)

class AppendToNode(Node):
	def __init__(self, nodelist, options):
		self.nodelist = nodelist
		self.options = options
		self.var = options['var']

	def __repr__(self):
		return "<AppendToNode>"

	def render(self, context):
		l = self.var.resolve(context)
		if self.options.get('as', None):
			t = self.options.get('type', None)
			if t == 'h':
				row = {}
			elif t == 'body':
				row = { 'rows': [] }
			else:
				row = []
			l.append(row)
			values = { self.options['as']: row }
			context.update(values)
			self.nodelist.render(context)
			context.pop()
		else:
			l.append(self.nodelist.render(context))
		return ''


@register.tag('set')
def do_set(parser, token):
	bits = token.contents.split()
	if len(bits) != 2:
		raise TemplateSyntaxError('%s requires a single argument defining the variable' % bits[0])
	var = Variable(bits[1])

	nodelist = parser.parse(('endset',))
	parser.delete_first_token()

	return SetNode(nodelist, var)

class SetNode(Node):
	def __init__(self, nodelist, var):
		self.nodelist = nodelist
		self.var = var

	def __repr__(self):
		return "<SetNode>"

	def render(self, context):
		v = self.var.var.split(VARIABLE_ATTRIBUTE_SEPARATOR)
		n = v.pop()
		if len(v) > 0:
			h = Variable(VARIABLE_ATTRIBUTE_SEPARATOR.join(v)).resolve(context)
			# @todo Support other types
			h[n] = self.nodelist.render(context)
		else:
			raise NotImplemented()
		return ''
