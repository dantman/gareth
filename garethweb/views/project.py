from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.validators import RegexValidator
from django import forms
from garethweb.pageview import GarethView, navigation
from garethweb.decorators import needs_right
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
	view = GarethView(request, ('project', 'create'))
	view.title = ("Create project",)
	view.set(add_form=form)
	view.crumb(Project, 'Create')
	return view()

class ProjectView(GarethView):
	def __init__(self, request, project, *args, **kwargs):
		GarethView.__init__(self, request, *args, **kwargs)
		self.project = project
		self.set(project=project)
		self.crumb(project)

	@property
	def tabs(self):
		return (
			{ 'href': reverse('project', kwargs={ 'name': self.project.name }), 'text': 'Project' },
			{ 'href': reverse('project_remotes', kwargs={ 'project': self.project.name }), 'text': 'Remotes' },
			{ 'href': reverse('remote_create', kwargs={ 'project': self.project.name }), 'text': 'Add remote' },
		)

def show(request, name):
	project = get_object_or_404(Project, name=name)
	view = ProjectView(request, project, ('project', 'show'))
	view.title = ("Project", ('project', project.name))
	return view()

@navigation('Projects', 1)
def index(request):
	projects = Project.objects.all()
	view = GarethView(request, ('project', 'index'))
	view.title = ("Projects",)
	view.set(projects=projects)
	view.crumb(Project)
	return view()
