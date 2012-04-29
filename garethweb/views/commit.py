from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from garethweb.models import Project
from garethweb.views.project import ProjectView

def _onecommit(f):
	def func(request, project, SHA1, *args, **kwargs):
		project = get_object_or_404(Project, name=project)
		commit = project.get_commit(SHA1)
		return f(request, project, commit, *args, **kwargs)
	func.__name__ = f.__name__
	return func

@_onecommit
def show(request, project, commit):
	view = ProjectView(request, project, ('commit', 'show'))
	view.title = ("Commit", ('commit', commit.sha1))
	view.set(commit=commit)
	view.crumb(commit)
	return view()
