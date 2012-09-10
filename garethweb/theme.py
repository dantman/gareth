# -*- coding: utf-8 -

themes = {}

class ThemeLoaderError(Exception):
	pass

def get(name):
	theme = themes.get(name, None)
	if not theme:
		raise ThemeLoaderError('There is no theme by the name %s.' % name)
	return theme

class Theme(object):
	def view_before_render(self, view):
		pass

def _theme(name):
	def _(cls):
		themes[name] = cls()
		return cls
	return _

# Themes
@_theme('bootstrap')
class BootstrapTheme(Theme):
	def view_before_render(self, view):
		view.use('theme.bootstrap')
