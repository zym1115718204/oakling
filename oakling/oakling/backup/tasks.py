from __future__ import absolute_import

import os

from celery import Celery
# from collector.utils import *

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oakling.settings')

from django.conf import settings  # noqa

app = Celery('oakling')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    return 200

#
# @app.task()
# def low_generator(project_id):
#     """
#     Celery Generator Task
#     :return:
#     """
#     generator = Generator(project_id)
#     result = generator.run_generator()
#     return result
#
#
# @app.task()
# def mid_generator(project_id):
#     """
#     Celery Generator Task
#     :return:
#     """
#     generator = Generator(project_id)
#     result = generator.run_generator()
#     return result
#
#
# @app.task()
# def high_generator(project_id):
#     """
#     Celery Generator Task
#     :return:
#     """
#     generator = Generator(project_id)
#     result = generator.run_generator()
#     return result
#
#
# @app.task()
# def low_processor(_id, project_id):
#     """
#     Celery Processor Task
#     :return:
#     """
#     processor = Processor(_id=_id, project_id=project_id)
#     result = processor.run_processor()
#     return result
#
#
# @app.task()
# def mid_processor(_id, project_id):
#     """
#     Celery Processor Task
#     :return:
#     """
#     processor = Processor(_id=_id, project_id=project_id)
#     result = processor.run_processor()
#     return result
#
#
# @app.task()
# def high_processor(_id, project_id):
#     """
#     Celery Processor Task
#     :return:
#     """
#     processor = Processor(_id=_id, project_id=project_id)
#     result = processor.run_processor()
#     return result