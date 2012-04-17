from django.shortcuts import render, redirect, get_object_or_404
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

def show(request, project, ID):
	project = get_object_or_404(Project, name=project)
	remote = get_object_or_404(Remote, project=project, name=ID)
	return render(request, 'remote/show.html', {
		'project': project,
		'remote': remote,
	})

def project(request, project):
	project = get_object_or_404(Project, name=project)
	remotes = Remote.objects.filter(project=project)
	return render(request, 'remote/project.html', {
		'project': project,
		'remotes': remotes,
	})
