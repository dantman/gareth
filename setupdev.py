#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
	filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gareth', 'settings_user.py')
	if not os.path.exists(filename):
		with open(filename, 'w') as f:
			f.write('from settings_auto_dev import *\n')
			f.write('\n')
			f.write("SECRET_KEY = '")
			f.write(os.urandom(60).encode('base64').replace('\n', '').encode('string_escape'))
			f.write("'\n")
