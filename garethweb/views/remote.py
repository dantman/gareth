from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import django.contrib.messages as m
from django.http import HttpResponse
from django import forms
from garethweb.models import Project, Remote
from garethweb.decorators import needs_right
import uuid
from hashlib import sha1

class RemoteForm(forms.ModelForm):
	class Meta:
		model = Remote
		fields = ['url']

@needs_right('contributor')
def create(request, project):
	project = get_object_or_404(Project, name=project)
	if request.method == 'POST':
		form = RemoteForm(request.POST)
		if form.is_valid():
			remote = form.save(commit=False)
			remote.project = project
			remote.user = request.user
			remote.name = sha1( "%s %s %s" % (remote.user.username, remote.url, uuid.uuid4().hex ) ).hexdigest()
			project.git.add_remote(remote.name, remote.url)
			remote.save()
			return redirect('remote', project=project.name, ID=remote.name)
	else:
		form = RemoteForm()
	return render(request, 'remote/create.html', {
		'project': project,
		'add_form': form
	})

def _oneremote(f):
	def func(request, project, ID, *args, **kwargs):
		project = get_object_or_404(Project, name=project)
		remote = get_object_or_404(Remote, project=project, name=ID)
		return f(request, remote, *args, **kwargs)
	func.__name__ = f.__name__
	return func

@_oneremote
def show(request, remote):
	return render(request, 'remote/show.html', {
		'project': remote.project,
		'remote': remote,
	})

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
	return render(request, 'remote/project.html', {
		'project': project,
		'remotes': remotes,
	})
