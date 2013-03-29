# -*- coding: utf-8 -
from hashlib import sha1
from urlparse import urlsplit
import uuid, re
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import django.contrib.messages as m
from django.http import HttpResponse
from django.utils.text import get_text_list
from django import forms
from garethweb.models import Project, Remote
from garethweb.decorators import needs_right
from garethweb.views.project import ProjectView
from garethweb.constants import SUPPORTED_GIT_PROTOCOLS

class DeleteConfirmForm(forms.Form):
	pass

class RemoteForm(forms.ModelForm):
	class Meta:
		model = Remote
		fields = ['url']

	def clean_url(self):
		data = self.cleaned_data['url']
		url = urlsplit(data)
		if not url.scheme and not url.netloc:
			m = re.match('^([^@]+@[^/]+):(.*)', url.path)
			if m:
				# user@host:... is equivalent to a ssh url
				url = urlsplit("ssh://%s/%s" % (m.group(1), m.group(2)))
		if not url.scheme:
			raise forms.ValidationError("The remote URL must be an absolute URL.")
		if url.scheme == 'ssh':
			raise forms.ValidationError("Gareth cannot fetch from ssh based remotes.")
		if url.scheme not in SUPPORTED_GIT_PROTOCOLS:
			raise forms.ValidationError("'%s' is not an acceptable url scheme. Gareth only accepts %s urls."
				% (url.scheme, get_text_list(SUPPORTED_GIT_PROTOCOLS, 'and')))

		return data

@needs_right('contributor')
def create(request, project):
	project = get_object_or_404(Project, name=project)
	if request.method == 'POST':
		form = RemoteForm(request.POST)
		if form.is_valid():
			remote = form.save(commit=False)
			remote.project = project
			remote.user = request.currentuser
			remote.name = sha1( "%s %s %s" % (remote.user.username, remote.url, uuid.uuid4().hex ) ).hexdigest()
			project.git.add_remote(remote.name, remote.url)
			remote.save()
			return redirect('remote', project=project.name, ID=remote.name)
	else:
		form = RemoteForm()
	view = ProjectView(request, project, ('remote', 'create'))
	view.title = ("Add remote to", ('project', project.name))
	view.activetab = 'addremote'
	view.set(add_form=form)
	view.crumb(Remote(project=project), 'Create')
	return view()

def _oneremote(f):
	def func(request, project, ID, *args, **kwargs):
		project = get_object_or_404(Project, name=project)
		remote = get_object_or_404(Remote, project=project, name=ID)
		return f(request, remote, *args, **kwargs)
	func.__name__ = f.__name__
	return func

@_oneremote
def show(request, remote):
	view = ProjectView(request, remote.project, ('remote', 'show'))
	view.title = ("Remote", ('remote', remote.name))
	view.activetab = 'remotes'
	view.set(project=remote.project, remote=remote)
	view.add_button(href=reverse('remote_fetch', kwargs={ 'project': remote.project.name, 'ID': remote.name }) + "?fromui=1", post=True, text='Fetch')
	if remote.user == request.currentuser:
		view.add_button(href=reverse('remote_delete', kwargs={ 'project': remote.project.name, 'ID': remote.name }), text='Delete')
	view.crumb(remote)
	view.use('remote-fetch-progress-alert')
	return view()

@_oneremote
def delete(request, remote):
	if request.method == 'POST':
		form = DeleteConfirmForm(request.POST)
		if form.is_valid():
			remote.delete()
			return redirect('project_remotes', project=remote.project.name)
	else:
		form = DeleteConfirmForm()
	view = ProjectView(request, remote.project, ('remote', 'delete'))
	view.title = ("Delete remote", ('remote', remote.name))
	view.activetab = 'remotes'
	view.set(remote=remote, form=form)
	view.crumb(remote)
	view.crumb('Delete')
	return view()

@csrf_exempt # must be first to work
@_oneremote
@require_POST
def fetch(request, remote):
	remote.queue_fetch()
	if 'fromui' in request.GET:
		m.success(request, 'Remote fetch queued')
		return redirect('remote', project=remote.project.name, ID=remote.name)
	else:
		return HttpResponse(status=204)

def project(request, project):
	project = get_object_or_404(Project, name=project)
	remotes = Remote.objects.filter(project=project)
	view = ProjectView(request, project, ('remote', 'project'))
	view.title = (('project', "%s's" % project.name), "remotes")
	view.activetab = 'remotes'
	view.set(remotes=remotes)
	view.crumb(Remote(project=project))
	return view()
