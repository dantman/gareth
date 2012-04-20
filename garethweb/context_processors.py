
def auth(request):
	return {
		'currentuser': request.currentuser,
	}
