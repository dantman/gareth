# -*- coding: utf-8 -
from collections import OrderedDict
from django.utils.encoding import StrAndUnicode, smart_str, smart_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe
from StringIO import StringIO
from garethweb import resources

class LoaderError(Exception):
	pass

class Style(StrAndUnicode):
	def __init__(self, src=None, source=None):
		self.src = src
		self.source = source

	@property
	def html(self):
		if self.src:
			return mark_safe('<link rel="stylesheet" href="%s">' % escape(resources.static(self.src)))
		self.source = smart_str(self.source)
		out = StringIO()
		out.write('<style>')
		if '\n' in self.source:
			out.write('\n')
		out.write(self.source)
		out.write('</style>')
		return mark_safe(smart_unicode(out.getvalue()))

	def __unicode__(self):
		return self.html

class Script(StrAndUnicode):
	def __init__(self, src=None, source=None):
		self.src = src
		self.source = source

	@property
	def html(self):
		if self.src:
			return mark_safe('<script src="%s"></script>' % escape(resources.static(self.src)))
		self.source = smart_str(self.source)
		out = StringIO()
		out.write('<script>')
		if '\n' in self.source:
			out.write('\n')
		out.write(self.source)
		out.write('</script>')
		return mark_safe(smart_unicode(out.getvalue()))

	def __unicode__(self):
		return self.html

class HtmlList(list, StrAndUnicode):
	def __unicode__(self):
		return mark_safe('\n'.join(map(lambda s: smart_unicode(s.html), self)))

class ResourceLoader(object):
	def __init__(self):
		self.resources = OrderedDict()

	def require(self, name):
		if name in self.resources:
			return

		resource = resources.get(name)
		if not resource:
			raise LoaderError("There is no resource by the name %s." % name)
		for requirement in resource.requirements:
			self.require(requirement)
		self.resources[resource.name] = resource

	@property
	def styles(self):
		s = HtmlList()
		for resource in self.resources.itervalues():
			for style in resource.styles:
				s.append(Style(**style))
		return s

	@property
	def scripts(self):
		s = HtmlList()
		for resource in self.resources.itervalues():
			for script in resource.scripts:
				s.append(Script(**script))
		return s
