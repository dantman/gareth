
namespace_modules = (
	'fetchprogress',
)

namespaces = {}

for name in namespace_modules:
	module = __import__("garethweb.sockets.%s" % name, fromlist=('endpoint', 'handler'), level=1)
	namespaces[module.endpoint] = module.handler
