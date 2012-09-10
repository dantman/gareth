# -*- coding: utf-8 -
import textwrap, json
from django.utils.encoding import smart_unicode
from urlparse import urljoin
from StringIO import StringIO
from gareth import settings

resources = {}

def static(path):
	return urljoin(settings.STATIC_URL, path)

def get(name):
	return resources.get(name, None)

class Resource(object):
	def __init__(self, name):
		self.name = name
		self.styles = []
		self.scripts = []
		self.requirements = []

def resource(name, **kwargs):
	res = Resource(name)

	# Styles
	if "style" in kwargs and "styles" not in kwargs:
		kwargs["styles"] = (kwargs["style"],)
	if "styles" in kwargs:
		for style in kwargs["styles"]:
			if isinstance(style, basestring):
				if "\n" in style:
					style = { "source": style }
				else:
					style = { "src": style }
			res.styles.append(style)

	# Scripts
	if "script" in kwargs and "scripts" not in kwargs:
		kwargs["scripts"] = (kwargs["script"],)
	if "scripts" in kwargs:
		for script in kwargs["scripts"]:
			if isinstance(script, basestring):
				if "\n" in script:
					script = { "source": script }
				else:
					script = { "src": script }
			res.scripts.append(script)

	if "variables" in kwargs:
		vs = StringIO()
		for var, value in kwargs["variables"].iteritems():
			vs.write('var ')
			vs.write(var)
			vs.write(' = ')
			if callable(value):
				value = value()
			vs.write(json.dumps(value))
			vs.write(';\n')
		varscript = smart_unicode(vs.getvalue())
		if varscript.find('\n') + 1 == len(varscript):
			varscript = varscript.rstrip('\n')
		res.scripts.append({ 'source': varscript })

	# Requirements
	if "require" in kwargs:
		require = kwargs["require"]
		if isinstance(require, basestring):
			require = (require,)
		for requirement in require:
			res.requirements.append(requirement)

	resources[res.name] = res

# Resources
resource(
	'jquery',
	script="js/jquery-1.7.2.min.js"
)

resource(
	'socketio',
	script="js/socket.io.js",
	variables={
		'WEB_SOCKET_SWF_LOCATION': lambda: "js/WebSocketMain.swf", # @todo This needs to be static relative
	}
)

resource(
	'pygments',
	style="../resources/pygments.css"
)

resource(
	'diff.css',
	style="css/diff.css",
	require='pygments'
)

resource(
	'bootstrap',
	styles=(
		"bootstrap/css/bootstrap.css",
		textwrap.dedent("""
		.breadcrumb li:before {
			color: #999999;
			padding: 0 5px;
			content: "/";
		}
		.breadcrumb li:first-child:before {
			display: none;
		}
		"""),
		"bootstrap/css/bootstrap-responsive.css",
	),
	require='jquery'
)

resource(
	'bootstrap.js',
	script="bootstrap/js/bootstrap.js",
	require='jquery'
)

resource(
	'theme.bootstrap',
	style="themes/bootstrap/css/theme.css",
	script="themes/bootstrap/js/theme.js",
	require=(
		'bootstrap',
		'bootstrap.js',
	)
)

resource(
	'remote-fetch-progress-alert',
	script="js/remote-fetch-progress-alert.js",
	require='socketio'
)
