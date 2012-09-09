# -*- coding: utf-8 -
from socketio import socketio_manage

def socketio_service(request):
	socketio_manage(request.environ, namespaces={}, request=request)

	return {}
