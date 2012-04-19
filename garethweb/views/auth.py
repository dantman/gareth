from django.shortcuts import render, redirect
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from garethweb.pageview import GarethView
from garethweb.models import User

class LoginForm(forms.Form):
	username = forms.CharField(max_length=255)
	password = forms.CharField(widget=forms.PasswordInput)

	def clean(self):
		cleaned_data = super(forms.Form, self).clean()
		cleaned_data['user'] = None
		try:
			if 'username' in cleaned_data:
				cleaned_data['user'] = User.objects.get( username=cleaned_data['username'] )
				if not cleaned_data['user'].compare_password(cleaned_data['password']):
					self._errors['password'] = self.error_class([u'Password is invalid.'])
		except ObjectDoesNotExist:
			self._errors['username'] = self.error_class([u'That user does not exist.'])
		return cleaned_data

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			request.session['user_id'] = form.cleaned_data['user'].id
			return redirect('home')
	else:
		form = LoginForm

	view = GarethView(request, ('auth', 'login'))
	view.title = ("Login",)
	view.set(form=form)
	view.crumb('Login')
	return view()

def logout(request):
	del request.session['user_id']
	return redirect('home')
