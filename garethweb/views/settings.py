from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.encoding import smart_unicode
from django import forms
from garethweb.pageview import GarethView
from garethweb.decorators import needs_user
from garethweb.models import User, UserEmail, UnconfirmedUserEmail
import os, binascii

class SettingsView(GarethView):
	def __init__(self, request, *args, **kwargs):
		GarethView.__init__(self, request, *args, **kwargs)
		self.title = ("Settings",)
		self.activenav = 'settings'
		self.crumb('Settings')
		self.set(theuser=request.currentuser)

	@property
	def tabs(self):
		return (
			{ 'name': 'profile', 'href': reverse('settings'), 'text': 'Profile' },
			{ 'name': 'identities', 'href': reverse('identities'), 'text': 'Identities' },
			{ 'name': 'remotes', 'href': reverse('my_remotes'), 'text': 'Remotes' },
		)

@needs_user
def profile(request):
	view = SettingsView(request, ('settings', 'profile'))
	view.activetab = 'profile'
	view.crumb('Profile')
	return view()

class EmailInput(forms.widgets.TextInput):
	input_type = 'email'
	def render(self, name, value, attrs=None):
		if not attrs:
			attrs = {}
		attrs['placeholder'] = name.replace('_', ' ').capitalize()
		return forms.widgets.TextInput.render(self, name, value, attrs)

class NewEmailForm(forms.ModelForm):
	email = forms.EmailField(widget=EmailInput)
	class Meta:
		model = UnconfirmedUserEmail
		fields = ['email']

@needs_user
def identities(request):
	user = request.currentuser
	if request.method == 'POST':
		form = NewEmailForm(request.POST)
		if form.is_valid():
			email = form.save(commit=False)
			email.user = user
			email.token = binascii.hexlify(os.urandom(32))
			email.save()
			# @todo Send confirmation email
			return redirect('identities')
	else:
		form = NewEmailForm()
	view = SettingsView(request, ('settings', 'identities'))
	view.activetab = 'identities'
	view.set(
		identities=user.useremail_set.all(),
		unconfirmed_identities=user.unconfirmeduseremail_set.all(),
		add_form=form
	)
	view.crumb('Identities')
	return view()

@needs_user
def remotes(request):
	view = SettingsView(request, ('settings', 'remotes'))
	view.activetab = 'remotes'
	view.set(remotes=request.currentuser.remote_set.all())
	view.crumb('Remotes')
	return view()
