from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from garethweb.decorators import needs_user
from garethweb.models import User, UserEmail, UnconfirmedUserEmail
import os, binascii

@needs_user
def profile(request):
	user = request.user
	return render(request, 'settings/profile.html', {
		'user': user,
	})

class NewEmailForm(forms.ModelForm):
	class Meta:
		model = UnconfirmedUserEmail
		fields = ['email']

@needs_user
def identities(request):
	user = request.user
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
	return render(request, 'settings/identities.html', {
		'user': user,
		'identities': user.useremail_set.all(),
		'unconfirmed_identities': user.unconfirmeduseremail_set.all(),
		'add_form': form
	})

@needs_user
def remotes(request):
	user = request.user
	return render(request, 'settings/remotes.html', {
		'user': user,
		'remotes': user.remote_set.all(),
	})
