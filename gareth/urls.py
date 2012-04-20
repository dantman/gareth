from django.conf.urls import patterns, include, url

urlpatterns = patterns('garethweb.views',
	# Home
    url(r'^$', 'home', name='home'),

    # Projects
    url(r'^projects/create$', 'project.create', name='project_create'),
    url(r'^projects/(?P<name>.+)$', 'project.show', name='project'),
    url(r'^projects$', 'project.index', name='projects'),

    # Remotes
    url(r'^remotes/(?P<project>.+)/create$', 'remote.create', name='remote_create'),
    url(r'^remotes/(?P<project>.+)/(?P<ID>[0-9a-fA-F]{40})/fetch$', 'remote.fetch', name='remote_fetch'),
    url(r'^remotes/(?P<project>.+)/(?P<ID>[0-9a-fA-F]{40})$', 'remote.show', name='remote'),
    url(r'^remotes/(?P<project>.+)$', 'remote.project', name='project_remotes'),

    # Users
    url(r'^users/(?P<username>.+)$', 'user.profile', name='user'),
    url(r'^users$', 'user.index', name='users'),
    url(r'^profile$', 'user.my_profile', name='profile'),

    # User
	url(r'^login$', 'auth.login', name='login'),
	url(r'^logout$', 'auth.logout', name='logout'),
	url(r'^settings$', 'settings.profile', name='settings'),
	url(r'^settings/identities$', 'settings.identities', name='identities'),
	url(r'^settings/remotes$', 'settings.remotes', name='my_remotes'),
)
