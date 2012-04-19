from garethweb.pageview import GarethView, navigation

@navigation('Homepage')
def home(request):
	view = GarethView(request, ('home',))
	view.title = ()
	view.crumb('home')
	return view()
