from hashlib import sha1
import uuid
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import django.contrib.messages as m
from django.http import HttpResponse
from django import forms
from garethweb.models import Project, Remote
from garethweb.decorators import needs_right
from garethweb.views.project import ProjectView

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
	view = ProjectView(request, project, ('remote', 'create'))
	view.title = ("Add remote to", ('project', project.name))
	view.set(project=project, add_form=form)
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
	view.set(project=remote.project, remote=remote)
	view.crumb(remote)
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
	view.set(project=project, remotes=remotes)
	view.crumb(Remote(project=project))
	return view()
