from django.shortcuts import redirect
from django.http import HttpResponseForbidden

class needs_right():
	def __init__(self, right):
		self.right = right

	def __call__(self ,f):
		def func(request, *args, **kwargs):
			if not request.user:
				# @todo Reverse target
				return redirect('login')
			if not request.user.rights[self.right]:
				# @todo Better error page
				return HttpResponseForbidden("This page requires the %s right" % self.right)
			return f(request, *args, **kwargs)
		func.__name__ = f.__name__
		return func

needs_user = needs_right('user')
