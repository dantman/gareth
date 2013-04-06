Gareth Code Review
==================
**Gareth** is a web based code review system intended to work with git repositories.

Gareth does not depend on any hacks requiring you to use verbose cli commands, custom programs that do not come with git (such as `git review`), or fragile commit message amendments (like `Change-Id:`).

Gareth is instead fundamentally based on the standard git practice of everyone pushing new commits to their own public repository and having project maintainers pull those changes into their own repository to review and then push them into the primary repository.

Under Gareth's model. Gareth takes the role of managing the primary repository. You push any changes you want into your own public repository — hosted anywhere you want. Commits are then pulled into a review area where other contributors and maintainers can review your code and test it out. When a maintainer has decided to accept your commit Gareth does the work of merging it into the primary repository.

## Installation and development
Gareth requires some fairly heavy dependencies to function correctly. If you are not installing this in production the best way to run Gareth is to use [Gareth Vagrant][] which will use Vagrant to setup a Virtual Machine and install Gareth and all of it's dependencies into that VM separate from the rest of your system.

## Requirements
Gareth is written in [Python][] using the [Django][] framework and requires python, some other python libraries, a SQL database, and a STOMP server to function.

### Python and libraries
Gareth is primarily run with Python 2.7 and has not been tested under Python 3. It also depends on gevent which does not currently have Python 3.

Gareth depends on these python libraries:
  * `gevent`
  * `gevent-socketio`
  * `gunicorn` # webserver
  * `django`
  * `south`
  * `pytz`
  * `pygments`
  * `diff-match-patch`
  * `stompest`

You can use `pip install -r requirements.txt` to install all the necessary modules.

If you wish to use MySQL as the database you will also need the `mysql-python` library.

### Database
Gareth stores most of it's data inside of a SQL database. It should work fine with any type of database that Django supports. But has been primarily developed against SQLite and MySQL.

### STOMP
Gareth uses a STOMP server to communicate events — such as repository fetch requests and progress updates — between web requests, extra processes like the taskrunner, and clients listening over socket.io connections.

Gareth is developed against the Apache [Apollo][] STOMP server and hasn't been tested at all against any other STOMP server.

## General setup
1. Create a settings file at `gareth/settings_user.py`; There is a `settings_user-sample.py` you can use as a base.
2. If using sqlite ensure the directory the database will live in exists. Otherwise make sure the database and db user exists and has the necessary permissions and you have the necessary python library for Django to talk to the database server.
3. Run `./manage.py syncdb` to initialize the database
4. Run `./manage.py migrate` to finish database setup
5. You can run `./manage.py createuser -a {username} {password}` to create an admin user to login with
6. Startup the Gunicorn webserver
7. Run `./manage.py taskrunner` to startup the Gareth task runner

## CSS
Editing of css files should not be done directly. Instead anyone modifying css should edit the .scss files and be running `sass --watch garethweb/public`.

## License
### Gareth code
Copyright © 2013 - Daniel Friesen

Gareth is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Gareth is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

A copy of the [GNU Affero General Public License][AGPL] is available inside the `AGPL` file.

Additionally when turning isolated parts of the Gareth codebase into libraries separate from Gareth. The code that is turned into a library may be relicensed under the [MIT License][], the latest version of the [Apache License][], the [LGPL][], or dual-licensed under the [GPL][] and the Apache License or MIT License.

### Documentation
In addition to whatever other license it may be under. Documentation within the Gareth codebase whether in the form of standalone documentation or in the form of code comments may be used under the [Creative Commons Attribution 3.0][CC-BY-3.0] license.

### Other code
Gareth contains some 3rd party libraries inside of it's codebase. These libraries are under different license terms than the rest of the Gareth codebase. These libraries, their information, and license terms can be found inside the `NOTICE.md` file.

 [Python]: http://www.python.org/
 [Django]: https://www.djangoproject.com/
 [Apollo]: https://activemq.apache.org/apollo/
 [Gareth Vagrant]: https://github.com/dantman/gareth-vagrant
 [MIT License]: http://opensource.org/licenses/MIT
 [Apache License]: http://www.apache.org/licenses/LICENSE-2.0
 [AGPL]: https://www.gnu.org/licenses/agpl-3.0.html
 [LGPL]: https://www.gnu.org/licenses/lgpl.html
 [GPL]: https://www.gnu.org/licenses/gpl.html
 [CC-BY-3.0]: https://creativecommons.org/licenses/by/3.0/
