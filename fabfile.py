from fabric.api import local
import fabric.contrib.project as project

ROOTDIR = '/home/egghead/projects/python/samesake'
MYNT_PATH = '/home/egghead/.virtualenvs/samesake/bin/mynt'
DEPLOY_PATH = '/home/egghead/public/samesake/log'
PROJECT_NAME = 'egglog'

def clean():
    local('rm -rf %s/_deploy' % ROOTDIR)

def generate():
    local('%s gen %s/_deploy' % (MYNT_PATH, ROOTDIR))

def deploy():
    local('cp -r %s/_deploy/* %s' % (ROOTDIR, DEPLOY_PATH))

def regen():
    clean()
    generate()

def redeploy():
    regen()
    deploy()
    clean()
