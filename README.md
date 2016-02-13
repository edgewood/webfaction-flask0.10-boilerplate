# Webfaction Flask 0.10 Boilerplate

This project will help you to start new [Flask](http://flask.pocoo.org/)
projects on [Webfaction](http://www.webfaction.com/).

It provides a boilerplate template for a Flask 0.10 project on Webfaction.
Clone it, customize the fabric\_settings.py.sample, run Fabric, and you'll
have:

 - a local Python venv with Flask and a minimal Flask app installed
 - a local Fabric deployment script set up to deploy your app
 - a local Git repository for that app, connected to...
 - a Git repository on Webfaction for the app 
 - a Flask app on Webfaction set up with a Python venv there
 - a static app on Webfaction to serve your static content efficiently

In short, it will create a local Flask development environment and a production
Flask environment on Webfaction, and hook the two together!

## Use with caution
This project is intended to save repetitive work for people who know how to
deploy a Flask app, not as an "easy button" for people who don't.  I've used
this project to create a working Flask app on Webfaction as of 2016-02-09, but
if something breaks, you'll need to read the output, read the fabfile, figure
out what went wrong (and open an issue here), and correct it.  The fab task
does try to remove previous failed attempts if it detects them.

## One-time setup

This project sets up a Git repository on Webfaction for each Flask app, for
source control and as the way Flask apps are deployed.  This requires a Git app
on Webfaction.  The app is created with:

``
fab onetime_setup
``

This step is only required for your first Flask app created with this project.

## Setup

First, clone this project into the directory that you want your new project to
live in.

``
    cd ~/Projects
    git clone git://github.com/edgewood/webfaction-flask0.10-boilerplate.git myproject
    cd myproject
``

Update the project settings file with your Webfaction and project details.

``
    cp fabric_settings.py.sample fabric_settings.py
    $EDITOR fabric_settings.py
``

These settings must be updated:

- ``ENV_USER`` - your Webfaction username.
- ``ENV_PASS`` - your Webfaction password.  Webfaction doesn't offer an API
  access token, so your password is required for the automated server setup.
  If you're uncomfortable writing this in, set to None and you'll be prompted
  for your password when it's needed.
- ``PROJECT_NAME`` - the name for this project.
- ``APP_DOMAIN`` - which of your domains to deploy the app on.
- ``APP_URL`` - the URL path to deploy the app on.  '/' for the root of the
  domain, or a path like '/foo'
  
These settings probably don't need to be changed.  They control which
application types are created.  See the 
[list of application types](https://docs.webfaction.com/xmlrpc-api/apps.html#application-types).

- ``APP_TYPE`` - type for the Flask app.  Might need to be changed for newer
  versions of mod\_wsgi or Python, or if you want Python 2.7.
- ``STATIC_TYPE`` - type for static app that allows more efficient serving of
  static content.
- ``GIT_TYPE`` - type for the Git app that serves Git repos.  Only relevant
  for ``onetime_setup``.

Settings related to the Python virtualenvs:

- ``VENV_NAME`` - name of the local and remote virtualenv.  Change if you
  don't like ``venv``.
- ``VENV_COMMAND`` - command to create virtualenv.  Change to the command to
  create`a virtualenv in your selected version of Python.

Finally, perform the local and remote setup:
``
    fab install_everything
``

This will:

- install the server environment
  - delete previous attempts, if any detected
  - add the Flask and static Webfaction applications
  - create a virtualenv
  - create a Git repository
  - clean up sample files in the new Webfaction applications 
  - add the applications to the appropriate website
- install the local environment
  - remove the boilerplate Git repo and create a new one
  - create a Flask project
  - create fabric deployment scripts for the project
  - commit the project to Git
- link the local Git repository to the remote
- install Flask requirements to the remote virtualenv
- deploy the app remotely

You now have the sample Flask app running locally and deployed remotely.
Update it with your desired behavior, test it locally, commit it to your local
Git repo, and `` fab deploy `` to push it to Webfaction and deploy it.
