"""Fabfile for webfaction-flask0.10-boilerplate``.

Make sure to setup your ``fabric_settings.py`` first. As a start, just copy
``fabric_settings.py.sample``.

"""
# Basic structure from https://github.com/bitmazk/webfaction-django1.4-boilerplate.git

from __future__ import with_statement

import getpass
import sys
import xmlrpclib

from fabric.api import (
    cd,
    env,
    get,
    lcd,
    local,
    path,
    put,
    run,
    settings,
    )
import fabric_settings as fab_settings

env.hosts = fab_settings.ENV_HOSTS
env.user = fab_settings.ENV_USER

PROJECT_NAME = fab_settings.PROJECT_NAME


# ****************************************************************************
# HIGH LEVEL TASKS
# ****************************************************************************
def install_everything():
    install_server()
    install_local_repo()
    local_link_repo_with_remote_repo()
    first_deployment()


def onetime_setup():
    """ only has to be done one time ever """
    api_add_git_domain()


def first_deployment():
    run_install_requirements()
    run_prepare_local_settings()
    run_deploy_website()


def install_local_repo():
    local_create_virtualenv()
    local_create_new_repo()
    local_init_flask_project()
    local_create_fab_settings()
    local_initial_commit()


def install_server():
    run_delete_previous_attempts()
    api_add_applications()
    run_create_virtualenv()
    run_create_git_repo()
    run_configure_static_application()
    api_add_app_to_website()


# ****************************************************************************
# LOCAL TASKS
# ****************************************************************************
def local_link_repo_with_remote_repo():
    with lcd(fab_settings.PROJECT_ROOT):
        local('git config http.sslVerify false')
        local('git config http.postBuffer 524288000')
        with settings(warn_only=True):
            local('git remote rm origin')
        local('git remote add origin'
              ' {0}@{0}.webfactional.com:'
              '/home/{0}/webapps/git/repos/{1}'.format(
                    fab_settings.ENV_USER, fab_settings.GIT_REPO_NAME))
        local('git push -u origin master')


def local_create_fab_settings():
    with lcd(fab_settings.PROJECT_ROOT):
        local('cp config/fabfile.py fabfile.py')
        local('cp config/fabric_settings.py fabric_settings.py')
        local('sed -i -e "s/@HOSTS@/{0}/"'
              ' -e "s/@USER@/{1}/"'
              ' -e "s!@REMOTE_APP_ROOT@!{2}!"'
              ' -e "s/@VENV@/{3}/"'
              ' -e "s/@APPNAME@/{4}/"'
              ' -e "s/@STATICNAME@/{5}/"'
              ' fabric_settings.py'.format(
                  repr(fab_settings.ENV_HOSTS),
                  fab_settings.ENV_USER,
                  fab_settings.REMOTE_APP_ROOT,
                  fab_settings.VENV_NAME,
                  fab_settings.APP_NAME,
                  fab_settings.STATIC_NAME,
                  ))


def local_create_new_repo():
    with lcd(fab_settings.PROJECT_ROOT):
        local('rm -rf .git')
        local('git init')

        gitignore = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]

# Distribution / packaging
{0}/
""".format(fab_settings.VENV_NAME)
        local('printf "{0}" >> .gitignore'.format(gitignore))


def local_init_flask_project():
    with lcd(fab_settings.PROJECT_ROOT):
        # download remote default Apache httpd.conf
        local('rm -rf apache2/conf')
        local('mkdir -p apache2/conf')
        with cd(fab_settings.REMOTE_APP_ROOT):
            get(remote_path='apache2/conf/httpd.conf',
                local_path ='apache2/conf/httpd.conf')

        # prepare httpd.conf
        app_root_fullpath = fab_settings.REMOTE_APP_ROOT_FULLPATH
        python_home = '{0}/{1}'.format(app_root_fullpath, fab_settings.VENV_NAME)
        # strip '/lib/'... from python-path so app dir is in python path
        local("sed -i -e '/^\s*WSGIDaemonProcess.*/ s@\(python-path=[^ ]\+\)/lib/[^ ]\+@\\1@'"
              " apache2/conf/httpd.conf")
        # add python-home pointed at the virtualenv
        local("sed -i -e '/^\s*WSGIDaemonProcess.*/ s@$@ python-home={0}@'"
              " apache2/conf/httpd.conf".format(python_home))
        # add script alias for index.py
        local("sed -i -e '/^\s*WSGIDaemonProcess.*/a "
              "WSGIScriptAlias / {0}/htdocs/index.py'"
              " apache2/conf/httpd.conf".format(app_root_fullpath))
        # prepare webfaction.py with APP_URL
        local("sed -i -e 's!@APP_URL@!{0}!'"
              " htdocs/webfaction.py".format(fab_settings.APP_URL))

        # initialize local Flask project
        with path('{0}/bin'.format(fab_settings.VENV_NAME), behavior='prepend'):
            local('pip install Flask')
            local('pip freeze > requirements.txt')


def local_initial_commit():
    with lcd(fab_settings.PROJECT_ROOT):
        flask_project_files = [
                '.gitignore',
                'requirements.txt',
                'fabfile.py',
                'fabric_settings.py',
                'apache2/',
                'myapp/',
                'htdocs/',
        ]
        for project_file in flask_project_files:
            local('git add "{0}"'.format(project_file))
        local('git commit -am "Initial commit."')
        # remove files not under version control
        local('git clean -d -f')


def local_create_virtualenv():
    with lcd(fab_settings.PROJECT_ROOT):
        local(fab_settings.VENV_COMMAND)


# ****************************************************************************
# REMOTE TASKS
# ****************************************************************************
def run_create_git_repo():
    run('rm -rf $HOME/webapps/git/repos/{0}'.format(fab_settings.GIT_REPO_NAME))
    with cd('$HOME/webapps/git'):
        run('git init --bare ./repos/{0}'.format(fab_settings.GIT_REPO_NAME))
    with cd('$HOME/webapps/git/repos/{0}'.format(fab_settings.GIT_REPO_NAME)):
        run('git config http.receivepack true')
        # pushes to remote repo deploys files to app root
        with cd('hooks'):
            hook_content = """
GIT_WORK_TREE={0} git checkout --force
""".format(fab_settings.REMOTE_APP_ROOT_FULLPATH)
            run('printf "%s" "{0}" > post-receive'.format(hook_content))
            run('chmod +x post-receive')


def run_create_ssh_dir():
    with cd('$HOME'):
        with settings(warn_only=True):
            run('mkdir .ssh')
            run('touch .ssh/authorized_keys')
            run('chmod 600 .ssh/authorized_keys')
            run('chmod 700 .ssh')


def run_configure_static_application():
    run('rm -f $HOME/webapps/{0}/index.html'.format(fab_settings.STATIC_NAME))


def run_delete_previous_attempts():
    api_remove_app_from_website()
    api_remove_applications()


def run_create_virtualenv():
    with cd(fab_settings.REMOTE_APP_ROOT):
        run(fab_settings.VENV_COMMAND)


def run_deploy_website():
    with lcd(fab_settings.PROJECT_ROOT):
        local('fab deploy')


def run_install_requirements():
    with cd(fab_settings.REMOTE_APP_ROOT):
        # site isn't deployed yet, so copy requirements.txt as one-off
        with lcd(fab_settings.PROJECT_ROOT):
            put(local_path='requirements.txt',
                remote_path ='requirements.txt')
        with path('{0}/bin'.format(fab_settings.VENV_NAME), behavior='prepend'):
            run('pip install -r requirements.txt')


def run_prepare_local_settings():
    # TODO update flask local settings file when I get that far
    pass


# ****************************************************************************
# WEBFACTION API TASKS
# ****************************************************************************

# a class to automatically add the session_id to Webfaction API calls 
# and provide related convenience methods
class _Webfaction:
    def __init__(self):
        self.server = None
        self.session_id = None


    def _add_session_id(self, fn):
        def wrap(*args):
            return fn(self.session_id, *args)
        return wrap


    def __getattr__(self, attr):
        # connect to server here instead of init to avoid connecting until necessary
        if self.session_id is None:
            self.server = xmlrpclib.ServerProxy('https://api.webfaction.com/')

            password = getattr(fab_settings, 'ENV_PASS', None)

            if password is None:
                password = getpass.getpass('Webfaction password: ')

            self.session_id, _ = self.server.login(fab_settings.ENV_USER, password)

        # hasattr(xmlrpclib_obj, X) returns True for any X, so is not useful here
        if attr in self.server.system.listMethods():
            return self._add_session_id(getattr(self.server, attr))
        else:
            raise AttributeError("class %s has no attribute '%s'" % (self.__class__.__name__, attr))


    def get_app(self, appname):
        return filter(lambda d: d['name'] == appname, self.list_apps())


    def app_exists(self, appname):
        return len(self.get_app(appname)) == 1


def api_add_applications():
    _webfaction_create_app(fab_settings.APP_NAME, fab_settings.APP_TYPE)
    _webfaction_create_app(fab_settings.STATIC_NAME, fab_settings.STATIC_TYPE)


def api_remove_applications():
    _webfaction_delete_app(fab_settings.APP_NAME)
    _webfaction_delete_app(fab_settings.STATIC_NAME)


def _webfaction_init(f):
    if not 'wf' in f.func_globals:
        f.func_globals['wf'] = _Webfaction() 

    return f


@_webfaction_init
def api_add_git_domain():
    """ add git.username.webfactional.com to username.webfactional.com """
    # get a list of sites that have the username site in subdomains
    username_site = '{0}.webfactional.com'.format(env.user)
    site = filter(lambda s: username_site in s['subdomains'], wf.list_websites())

    # if there is one, add git.username.webfactional.com to the subdomains
    if site:
        site = site[0]
        git_site = 'git.{0}'.format(username_site)

        if git_site not in site['subdomains']:
            # create domain
            wf.create_domain(username_site, 'git')

            # create app
            _webfaction_create_app('git', fab_settings.GIT_TYPE, 
                    app_extra=fab_settings.ENV_PASS)

            # create website with new domain and app
            site['subdomains'].append(git_site)
            wf.create_website('git', site['ip'], True,
                    ['git.{}'.format(username_site)], ['git', '/'])
    else:
        print "Could not add {0} to webfaction {1}".format(git_site, username_site)
        sys.exit(1)


@_webfaction_init
def _webfaction_update_website_apps(apps_updater):
    """ add app to website """
    # find websites that have the domain
    domain = fab_settings.APP_DOMAIN
    site = filter(lambda s: domain in s['subdomains'], wf.list_websites())

    if site:
        site = site[0]

        # call apps_updater to make changes to apps list
        apps = apps_updater(site['website_apps'])

        # update site with (possibly) changed apps list
        wf.update_website(site['name'], site['ip'], site['https'],
                site['subdomains'], *apps)
    else:
        print "Could not add {0} to {1}".format(fab_settings.APP_NAME, domain)
        sys.exit(1)


def _static_url(url):
    if url[-1] == '/':
        return '{0}static'.format(url)
    else:
        return '{0}/static'.format(url)


site_apps = (
        # Flask app on APP_URL
        ( fab_settings.APP_NAME, fab_settings.APP_URL, ),
        # Static app on APP_URL/static
        ( fab_settings.STATIC_NAME, _static_url(fab_settings.APP_URL), ),
    )


@_webfaction_init
def api_add_app_to_website():
    def app_add(apps):
        for app in site_apps:
            name = app[0]
            url = app[1]

            if not filter(lambda a: name == a[0] and url == a[1], apps):
                apps.append([name, url])

        return apps

    _webfaction_update_website_apps(app_add)


@_webfaction_init
def api_remove_app_from_website():
    def app_remove(apps):
        for app in site_apps:
            name = app[0]
            url = app[1]

            # filter out apps that match name and URL
            apps = filter(lambda a: not( name == a[0] and url == a[1] ), apps)

        return apps

    _webfaction_update_website_apps(app_remove)


@_webfaction_init
def _webfaction_create_app(app_name,app_type,app_extra=''):
    """creates a app on webfaction of the named type using the webfaction public API."""
    try:
        if not wf.app_exists(app_name):
            response = wf.create_app(app_name, app_type, False, app_extra)
            print "App on webfaction created: %s" % response
            return response
        else:
            print("App name {0} already in use".format(app_name))

    except xmlrpclib.Fault:
        print "could not create app %s on webfaction, app name maybe already in use" % app_name
        sys.exit(1)


@_webfaction_init
def _webfaction_delete_app(app_name):
    """deletes a named app on webfaction using the webfaction public API."""
    try:
        if wf.app_exists(app_name):
            with cd(fab_settings.REMOTE_APP_BASE.format(app_name)):
                run("if test -x apache2/bin/stop; then apache2/bin/stop; fi")
            response = wf.delete_app(app_name)
            print "App on webfaction deleted: %s" % response
            return response

    except xmlrpclib.Fault:
        print "could not delete app on webfaction %s" % app_name
        return False
