from garethweb.pageview import GarethView, navigation

@navigation('Homepage', order=0)
def home(request):
	view = GarethView(request, ('home',))
	view.title = ()
	view.activenav = 'home'
	view.crumb('home')
	return view()
