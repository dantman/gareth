# -*- coding: utf-8 -
from socketio import socketio_manage
from garethweb.sockets import namespaces

def socketio_service(request):
	socketio_manage(request.environ, namespaces=namespaces, request=request)

	return {}
