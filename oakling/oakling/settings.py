"""
Django settings for oakling project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

from common import *


# --------------------------------------------------------------------
# Version Info
# --------------------------------------------------------------------
# Version Info
VERSION = 'Oakling 1.0'


# --------------------------------------------------------------------
# MongdDB Settings
# --------------------------------------------------------------------
# Mongodb settings
MongoDBS = {
    'oakling_project': {
        'host': 'mongodb://localhost/oakling_project',
    },
    'oakling_task': {
        'host': 'mongodb://localhost/oakling_task',
    }
}

from mongoengine import connect  # noqa

for name, db in MongoDBS.iteritems():
    connect(host=db['host'], alias=name)


# --------------------------------------------------------------------
# APP Tree Settings
# --------------------------------------------------------------------
REGISTER_DATASYSTEMS = [
    "LOCAL",
    "HDFS",
]

# default, Tree root url;
BASETREE_URL = "/dashboard/data/"

# default, Local File data directory
LOCAL_DATAFILE_DIRS = os.path.join(os.path.dirname(BASE_DIR), "data")

# default hdfs data settings
HDFS_NAMENODE_HOST = "namenode"
HDFS_NAMENODE_PORT = 8020
HDFS_DATAFILE_DIRS = os.path.join("/tmp", "data")


# --------------------------------------------------------------------
# Utils Settings
# --------------------------------------------------------------------
# Spiders Path
PROJECTS_PATH = os.path.join(os.path.dirname(BASE_DIR), "projects")

# Execute Path
EXECUTE_PATH = os.path.join(BASE_DIR, "execute")


# --------------------------------------------------------------------
# Celery settings
# --------------------------------------------------------------------
# BROKER_URL = 'amqp://guest:guest@localhost//'
BROKER_URL = 'redis://localhost:6379/0'
ANALYSIS_REDIS = 'redis://localhost:6379/1'
NODES_REDIS = 'redis://localhost:6379/1'

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)

# BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_ENABLE_UTC = True

CELERY_ROUTES = {
         'oakling.celery.debug_task': 'test',
         'collector.tasks.low_processor': 'low_processor',
         'collector.tasks.mid_processor': 'mid_processor',
         'collector.tasks.high_processor': 'high_processor',
 }

CELERY_ANNOTATIONS = {
    'collector.tasks.low_processor': {'rate_limit': '6000/m'},
    'collector.tasks.mid_processor': {'rate_limit': '6000/m'},
    'collector.tasks.high_processor': {'rate_limit': '6000/m'},
    'oakling.celery.debug_task': {'rate_limit': '6000/m'},
}

CELERY_IMPORTS = (
    'oakling.celery',
    'collector.tasks',
)