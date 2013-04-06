Gareth Code Review
==================
**Gareth** is a web based code review system intended to work with git repositories.

Gareth does not depend on any hacks requiring you to use verbose cli commands, custom programs that do not come with git (such as `git review`), or fragile commit message amendments (like `Change-Id:`).

Gareth is instead fundamentally based on the standard git practice of everyone pushing new commits to their own public repository and having project maintainers pull those changes into their own repository to review and then push them into the primary repository.

Under Gareth's model. Gareth takes the role of managing the primary repository. You push any changes you want into your own public repository — hosted anywhere you want. Commits are then pulled into a review area where other contributors and maintainers can review your code and test it out. When a maintainer has decided to accept your commit Gareth does the work of merging it into the primary repository.

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

## Setup
1. Create a settings file at `gareth/settings_user.py`; There is a `settings_user-sample.py` you can use as a base.
2. If using sqlite ensure the directory the database will live in exists. Otherwise make sure the database and db user exists and has the necessary permissions and you have the necessary python library for Django to talk to the database server.
3. Run `./manage.py syncdb` to initialize the database
4. Run `./manage.py migrate` to finish database setup
5. You can run `./manage.py createuser -a {username} {password}` to create an admin user to login with
6. For development you can run `./manage.py runserver` to start up a development server on localhost

<em>Sorry, this information is a little out of date. Gunicorn should be run instead of the normal wsgi server. There's a second taskrunner process that should be run. And Gareth requires a STOMP server to function completely.</em>

## Developer quick install
The quickest pattern to try out Gareth or help out with it's development is to do this:
```shell
# Clone Gareth and cd into the correct directory
$ virtualenv .
$ source bin/activate
$ pip install -r requirements.txt
$ ./setupdev.py
$ ./manage.py syncdb
$ ./manage.py migrate
$ ./manage.py createuser -a admin admin
$ ./manage.py run_gunicorn -c gareth/gunicorn_config.py
# In another terminal
$ ./manage.py taskrunner
```

This will setup an isolated virtualenv. Install the packages necessary for Gareth. Install Gareth. Create an admin:admin user for you. And then start a webserver on localhost.

<em>Sorry, this information is a little out of date. Gareth and the taskrunnerm requires a configured STOMP server to function completely which is not included .</em>

## CSS
Editing of css files should not be done directly. Instead anyone modifying css should edit the .scss files and be running `sass --watch garethweb/public`.

 [Python]: http://www.python.org/
 [Django]: https://www.djangoproject.com/
 [Apollo]: https://activemq.apache.org/apollo/
