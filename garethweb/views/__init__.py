from garethweb.pageview import GarethView, navigation

@navigation('Homepage', 0)
def home(request):
	view = GarethView(request, ('home',))
	view.title = ()
	view.crumb('home')
	return view()
