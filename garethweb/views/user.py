from django.shortcuts import redirect, get_object_or_404
from garethweb.pageview import GarethView, navigation
from garethweb.decorators import needs_user
from garethweb.models import User

def profile(request, username):
	user = get_object_or_404(User, username=username)
	view = GarethView(request, ('user', 'profile'))
	view.title = ("User", ('user', user.username))
	view.activenav = 'users'
	view.set(theuser=user)
	view.crumb(user)
	return view()

@needs_user
def my_profile(request):
	return redirect('user', username=request.currentuser.username)

@navigation('Users', order=25, key='users')
def index(request):
	users = User.objects.all()
	view = GarethView(request, ('user', 'index'))
	view.title = ("Users",)
	view.activenav = 'users'
	view.set(users=users)
	view.crumb(User)
	return view()
