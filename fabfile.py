from fabric.api import *
from fabric.colors import red
from fabric.contrib.console import confirm

env.hosts = ['salt'] # assuming kvmate is located on your salt master
env.code_dir = '/home/kvmate/src' # location from the default deploy
env.gunicorn_pidfile = '/home/kvmate/run/gunicorn.pid'

#################################################
### Django interactions
#################################################
@task
def shell():
    with cd(env.code_dir):
        sudo('../bin/python kvmate/manage.py shell', user='kvmate')

@task
def syncdb():
    with cd(env.code_dir):
        sudo('../bin/python kvmate/manage.py syncdb', user='kvmate')

@task
def resetdb():
    if not confirm('This will delete ' + red('all') + ' contents from the database and resync it. Continue?', default=False):
        abort('Aborting at user request.')
    stop_gunicorn()
    stop_huey()
    sudo('dropdb kvmate', user='postgres')
    sudo('createdb kvmate -O kvmate', user='postgres')
    syncdb()
    start_gunicorn()
    start_huey()

@task
def schemamigration(app=None, initial=False, update=False):
    if app is None:
        abort('No app supplied.')
    with cd(env.code_dir):
        operations = '--initial' if initial else '--auto'
        if update:
            operations = operations + ' --update'
        sudo('../bin/python kvmate/manage.py schemamigration %s %s' % (app, operations), user='kvmate')

@task
def migrate(app=None):
    if app is None:
        abort('No app supplied.')
    with cd(env.code_dir):
        sudo('../bin/python kvmate/manage.py migrate %s' % app, user='kvmate')

#################################################
# Deployment
#################################################
@task
def test():
    with settings(warn_only=True):
        result = local('./manage.py test kvmate', capture=True)
    if result.failed and not confirm('Tests failed. Continue anyway?'):
        abort('Aborting at user request.')

@task
def commit():
    local('git add -p && git commit')

@task
def push():
    local('git push')

@task
def prepare_deploy():
    test()
    commit()
    push()

@task
def deploy(refresh_huey=False):
    if confirm('Deploying to production. Continue?'):
        with cd(env.code_dir):
            sudo('git pull', user='kvmate')
        reload_gunicorn()
        if refresh_huey:
            restart_huey()
        else:
            print('If you changed a \'tasks.py\' you will have to restart huey, too.')

@task(alias='gunicorn')
def reload_gunicorn():
    sudo('kill -HUP `cat %s`' % env.gunicorn_pidfile, user='kvmate')

@task(alias='huey')
def restart_huey():
    sudo('supervisorctl restart kvmate_huey')

#################################################
# Other
#################################################
@task
def start_gunicorn():
    sudo('supervisorctl start kvmate_gunicorn')

@task
def stop_gunicorn():
    sudo('supervisorctl stop kvmate_gunicorn')

@task
def start_huey():
    sudo('supervisorctl start kvmate_huey')

@task
def stop_huey():
    sudo('supervisorctl stop kvmate_huey')
