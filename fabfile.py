from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['salt']
env.code_dir = '/home/kvmate/src'

@task
def test():
    with settings(warn_only=True):
        result = local('./manage.py test kvmate', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

@task
def commit():
    local("git add -p && git commit")

@task
def push():
    local("git push")

@task
def prepare_deploy():
    test()
    commit()
    push()

@task
def deploy():
    if not confirm("Deploying to production. Continue?"):
        sys.exit(0)
    with cd(env.code_dir):
        sudo("git pull", user="kvmate")
    sudo("kill -HUP `cat /home/kvmate/run/gunicorn.pid`")
    sudo("supervisorctl restart kvmate_huey")
