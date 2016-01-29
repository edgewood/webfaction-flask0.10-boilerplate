from __future__ import with_statement

import sys
import xmlrpclib

from fabric.api import (
    cd,
    env,
    local,
    path,
    run,
    )
import fabric_settings as fab_settings

env.hosts = fab_settings.ENV_HOSTS
env.user = fab_settings.ENV_USER

def restart():
    with cd(fab_settings.REMOTE_APP_ROOT):
        run("apache2/bin/restart")


def deploy():
    local('git push origin')
    with cd(fab_settings.REMOTE_APP_ROOT):
        with path('{0}/bin'.format(fab_settings.VENV_NAME), behavior='prepend'):
            run('pip install --upgrade -r requirements.txt')
    restart()


def rollback():
    local('echo rollback not implemented yet')
    restart()
