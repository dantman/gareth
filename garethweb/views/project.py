from django.shortcuts import render, redirect, get_object_or_404
from django.core.validators import RegexValidator
from garethweb.decorators import needs_right
from django import forms
from garethweb.models import Project

class ProjectForm(forms.ModelForm):
	name = forms.CharField(validators=[
		RegexValidator(r'^[-_a-zA-Z0-9]+(/[-_a-zA-Z0-9]+)*$',
			message='Name must be a valid path: Alphanumeric characters, _, and - are permitted. / is permitted as a directory separator.',
			code='invalid-name')
	])
	class Meta:
		model = Project

	def clean_name(self):
		return self.cleaned_data['name']

@needs_right('project_admin')
def create(request):
	if request.method == 'POST':
		form = ProjectForm(request.POST)
		if form.is_valid():
			project = form.save(commit=False)
			project.git.initialize()
			project.save()
			return redirect('project', name=project.name)
	else:
		form = ProjectForm()
	return render(request, 'project/create.html', { 'add_form': form })

def show(request, name):
	project = get_object_or_404(Project, name=name)
	return render(request, 'project/show.html', { 'project': project })

def index(request):
	projects = Project.objects.all()
	return render(request, 'project/index.html', { 'projects': projects })
