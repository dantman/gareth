from django.conf.urls import patterns, include, url

urlpatterns = patterns('garethweb.views',
	# Home
    url(r'^$', 'home', name='home'),

    # Commits
    url(r'^p/(?P<project>.+).git/commit/(?P<SHA1>[0-9a-fA-F]{40})$', 'commit.show', name='commit'),

    # Remotes
    url(r'^p/(?P<project>.+).git/remotes/create$', 'remote.create', name='remote_create'),
    url(r'^p/(?P<project>.+).git/remotes/(?P<ID>[0-9a-fA-F]{40})/fetch$', 'remote.fetch', name='remote_fetch'),
    url(r'^p/(?P<project>.+).git/remotes/(?P<ID>[0-9a-fA-F]{40})/delete$', 'remote.delete', name='remote_delete'),
    url(r'^p/(?P<project>.+).git/remotes/(?P<ID>[0-9a-fA-F]{40})$', 'remote.show', name='remote'),
    url(r'^p/(?P<project>.+).git/remotes$', 'remote.project', name='project_remotes'),

    # Projects
    url(r'^p/create$', 'project.create', name='project_create'),
    url(r'^p/(?P<name>.+).git$', 'project.show', name='project'),
    url(r'^p$', 'project.index', name='projects'),

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
