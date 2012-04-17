
import os

INSTALLED_APPS = (
#    'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.humanize',
#    'django.contrib.messages',
#    'django.contrib.staticfiles',
	'garethweb',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.gzip.GZipMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	# 'django.contrib.messages.middleware.MessageMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'garethweb.middleware.AuthenticationMiddleware',
)

TEMPLATE_DIRS = (
	os.path.dirname( os.path.abspath( __file__ ) ) + '/templates'
)

ROLE_HIERARCHY = {
	'user': ['contributor'],
	'admin': ['project_admin'],
}