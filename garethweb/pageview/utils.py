import threading

# Due to a fault in Drupal {% extend %} always uses the global loader to load templates.
# This means that unless you rewrite extend and hack it into the default loader you cannot
# pass any template dir context that would allow you to load different templates depending
# on the theme used in the current requet.
# Unfortunately this means that we need to store the request inside the local thread (to avoid
# any issue with requests in other threads) and retrieve it inside of our template loader.

_local_thread = threading.local()

def set_request(request):
	_local_thread.request = request

def get_request():
	return getattr(_local_thread, 'request', None)
