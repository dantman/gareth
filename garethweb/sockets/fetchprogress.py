from socketio.namespace import BaseNamespace

class FetchProgressListener(BaseNamespace):
	def initialize(self):
		pass

	def on_subscribe(self, remote=None):
		pass

endpoint = '/fetchprogress'
handler = FetchProgressListener
