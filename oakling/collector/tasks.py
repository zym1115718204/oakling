from __future__ import absolute_import

import os

from celery import Celery
from collector.utils import Processor

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oakling.settings')

from django.conf import settings  # noqa

app = Celery('oakling')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task()
def low_processor(project_name, **args):
    """
    Celery  Processor Task
    :return:
    """
    processor = Processor()
    result = processor.run_processor(project_name, **args)
    return result

@app.task()
def mid_processor(project_name, **args):
    """
    Celery  Processor Task
    :return:
    """
    processor = Processor()
    result = processor.run_processor(project_name, **args)
    return result

@app.task()
def high_processor(project_name, **args):
    """
    Celery  Processor Task
    :return:
    """
    processor = Processor()
    result = processor.run_processor(project_name, **args)
    return result
