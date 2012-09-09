# -*- coding: utf-8 -
import os

INSTALLED_APPS = (
#    'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.humanize',
	'django.contrib.messages',
    'django.contrib.staticfiles',
	'garethweb',
	'south', # Database migrations
	'gunicorn',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.gzip.GZipMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'garethweb.middleware.AuthenticationMiddleware',
	'garethweb.pageview.middleware.ThemeMiddleware',
)

SESSION_COOKIE_HTTPONLY = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

TEMPLATE_DIRS = (
	os.path.dirname( os.path.abspath( __file__ ) ) + '/templates',
)

TEMPLATE_LOADERS = (
	('garethweb.pageview.template.Loader', (
		'django.template.loaders.filesystem.Loader',
	)),
    'django.template.loaders.filesystem.Loader',
#    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.core.context_processors.tz",
	"django.contrib.messages.context_processors.messages",
	"garethweb.context_processors.auth",
)

STATIC_ROOT = os.path.dirname( os.path.abspath( __file__ ) ) + '/public'
STATICFILES_DIRS = ( STATIC_ROOT, )

ROLE_HIERARCHY = {
	'user': ['contributor'],
	'admin': ['project_admin'],
}

DEFAULT_THEME = 'bootstrap'
