
# Enable development settings
from settings_dev import *

# Make this unique, and don't share it with anybody.
SECRET_KEY = [...]

REPO_PATH = [...]

# Use secure cookies (only do this if using https://)
SESSION_COOKIE_SECURE = True

# Setup the database
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': '',                      # Or path to database file if using sqlite3.
		'USER': '',                      # Not used with sqlite3.
		'PASSWORD': '',                  # Not used with sqlite3.
		'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
		'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
	}
}

# Setup the message queue system
STOMP = {
	'host': ('localhost', 61613),
	'user': '',
	'pass': '',
}
