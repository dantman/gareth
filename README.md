Gareth
======
Gareth is a commit review system for git.

Some of the fundamental focuses of Gareth are:
* Fetch based commit review; Git is made intending users to push to their own personal public repos. We should follow that model to in review. Gareth should be the only one directly modifying the repos inside Gareth.
* Ease of use; Even though Gareth's repo and user's repos are not on the same servers. There is nothing stoping us from incorporating a lot of automatic handling, conventions, and helpers to make review as easy as if you were pushing directly to Gareth.
* Branching, not amending; Git is designed to handle branding very well. And development of fixes follows the pattern of adding fixes to that. Users shouldn't be forced to modify existing commits and ruin the history of a repo in order to update a set of changes for review.

Requirements
------------

Garethis currently built on top of Symfony2.
* PHP 5.3.2 and up is required.
* Any database supported by Doctrine.
* Git must be installed in your system's PATH.

Installation
------------

Gareth is still barely written so there isn't much on installation yet, for now:

# Clone Gareth and point your webservers document root to /web
# Run `php bin/vendor install`
# Setup a folder to host your git repos in.
# Give the webserver write permission to /app/cache/* /app/logs/* and the directory you set your git repos up in.
# Copy app/config/parameters.ini.sample to app/config/parameters.ini and fill in a secret key value.
# Copy one of app/config/parameters.yml.sample or app/config/parameters.yml.sqlite to app/config/parameters.yml
## Setup database configuration inside of parameters.yml
## Configure repo_path with the path to the directory you setup for your git repos.
# Setup rewrite rules on your server:
## Paths that do not exist should point to /web/app.php or /web/app_dev.php (for local development)
## Another rule for / will be needed or you will need to set app.php or app_dev.php as the index in your webserver config (there is no index.php)
## /r should be aliased to your repos directory.
