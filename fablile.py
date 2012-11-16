""" Deployment of project.
"""

from fabric.api import *

env.hosts = ['host']
env.user = "user"

def update_django_project():

    with cd('/path/to/txtr'):
        run('git pull')
        with prefix('source /path/to/txtrenv/bin/activate'):
            run('pip install -r requirements.txt')
            run('python manage.py syncdb')
            run('python manage.py collectstatic --noinput')

def restart_webserver():

    sudo("service uwsgi restart")
    sudo("/etc/init.d/nginx restart")

def deploy():
   
    update_django_project()
    restart_webserver()