# This module can be imported into settings_user using
#   from settings_auto_dev import *
# To setup a basic automatic dev environment.
# This will:
#   - Import settings_dev
#   - Setup a sqlite database at {root}/dbs/dev.sqlite
#   - Setup a repo root at {root}/repos/
# Note that you will still need to define the SECRET_KEY yourself

import os

# Import the developer settings
from settings_dev import *

__root__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure a database
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(__root__, 'dbs/dev.sqlite'),
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}
if not os.path.exists(DATABASES['default']['NAME']):
	os.makedirs(DATABASES['default']['NAME'])

# Configure the repository path
REPO_PATH = os.path.join(__root__, 'repos')
if not os.path.exists(REPO_PATH):
	os.makedirs(REPO_PATH)
