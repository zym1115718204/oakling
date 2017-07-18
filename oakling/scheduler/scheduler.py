#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.24


import json
import time
import click
import datetime
import schedule
import threading

from collector import tasks
from collector.handler import Handler
from libs.database.mongodb.projectdb import Project

from django.conf import settings


class Scheduler(object):
    """
    Oakling Scheduler Module
    """
    def __init__(self):
        """
        Models Initialization
        """
        # Project.object(status=STATUS_ON).order_by('+priority')
        activate = settings.BASE_DIR

    # @staticmethod
    # def _filter_generator_projects():
    #     """
    #     Projects Filter
    #     :return:
    #     """
    #     _projects = Project.objects(status=Project.STATUS_ON).order_by('+priority')
    #     projects = []
    #     for project in _projects:
    #         now = datetime.datetime.now()
    #         last = project.last_generator_time
    #         interval = int(project.generator_interval)
    #         if not project.last_generator_time:
    #             projects.append(project)
    #             project.update(last_generator_time=now)
    #             continue
    #         next = last + datetime.timedelta(seconds=interval)
    #         if next <= now:
    #             projects.append(project)
    #             project.update(last_generator_time=now)
    #         else:
    #             continue
    #
    #     return projects

    @staticmethod
    def _filter_drop_project():
        """
        Filter delete group project
        :return:
        """
        _projects = Project.objects(status=Project.STATUS_DELAY)
        return _projects


    @staticmethod
    def _filter_processor_projects():
        """
        Projects Filter
        :return:
        """
        _projects = Project.objects(status=Project.STATUS_ON).order_by('+priority')
        projects = []
        for project in _projects:
            now = datetime.datetime.now()
            last = project.last_generator_time
            interval = int(project.generator_interval)
            if not project.last_generator_time:
                projects.append(project)
                project.update(last_generator_time=now)
                continue
            next = last + datetime.timedelta(seconds=interval)
            if next <= now:
                projects.append(project)
                project.update(last_generator_time=now)
            else:
                continue

        return projects

    # @staticmethod
    # def _filter_processor_projects():
    #     """
    #     Projects Filter
    #     :return:
    #     """
    #     _projects = Project.objects(status=Project.STATUS_ON).order_by('+priority')
    #     projects = []
    #     for project in _projects:
    #         projects.append(project)
    #
    #     return projects

    # def run_generator_dispatch(self):
    #     """
    #     Generator Dispatch
    #     :return:
    #     """
    #     projects = self._filter_generator_projects()
    #     for project in projects:
    #         _priority = project.priority
    #         if _priority == -1:
    #             celery.high_generator.delay(str(project.id))
    #         elif _priority <= 3:
    #             celery.mid_generator.delay(str(project.id))
    #         else:
    #             celery.low_generator.delay(str(project.id))
    #
    #     result = {
    #         'status': True,
    #         "projects": len(projects)
    #     }
    #
    #     print "[{0}]::Generator Dispatch::{1}".format(str(datetime.datetime.now())[:-4], result)
    #     return result

    # @staticmethod
    # def _filter_tasks(project):
    #     """
    #     Filter Tasks by Project
    #     :return:
    #     """
    #     _name = project.name
    #
    #     _num = project.downloader_dispatch
    #     exec("from execute.{0}_models import {1}Task".format(_name, str(_name).capitalize()))
    #     exec("tasks = {0}Task.objects(status=0)[0:{1}]".format(str(_name).capitalize(), int(_num)))
    #
    #     return tasks

    @staticmethod
    def _processor_tasks(project):
        """
        Dispatch Tasks by Project
        :return:
        """
        _priority = project.priority
        args = json.loads(project.args)
        if _priority == -1:
            tasks.high_processor.delay(project.name, **args)
        elif _priority <= 3:
            tasks.mid_processor.delay(project.name, **args)
        else:
            tasks.low_processor.delay(project.name, **args)

        return {
            "project": str(project.name),
         }

    def run_processor_dispatch(self):
        """
        Processor Dispatch
        :return:
        """
        results = []
        projects = self._filter_processor_projects()

        for project in projects:
            # tasks = self._filter_tasks(project)
            result = self._processor_tasks(project)
            results.append(result)

        now = str(datetime.datetime.now())[:-4]
        info = "[ Scheduler {0}]::Processor Dispatch::{1} ::{2}".format(now, len(results), results)
        click.secho("[ INFO ] %s" % info, fg='green', bg='black')

        return results


    def run_auto_drop_project(self):
        """
        Auto drop project
        :return:
        """
        results = []
        handler = Handler()
        projects = self._filter_drop_project()

        for project in projects:
            if project.group == "delete" or "Delete" or "DELETE":
                result = handler.drop_project(project.name)
                results.append(result)

        now = str(datetime.datetime.now())[:-4]
        info = "[ Scheduler {0}]::Drop Project::{1} ::{2}".format(now, len(results), results)
        click.secho("[ INFO ] %s" % info, fg='red', bg='black')

        return results

    @staticmethod
    def run_query_project_status():
        """
        Run Query Project Status to Redis
        :return:
        """
        handler = Handler()
        results = handler.query_all_projects_status("--all")
        now = str(datetime.datetime.now())[:-4]
        info = "[ Scheduler {0}]::Analysis  Dispatch::{1} Updated Success.".format(now, len(results))
        click.secho("[ INFO ] %s" % info, fg='yellow', bg='black')

    @staticmethod
    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()
        # print threading.enumerate()

    def run(self):
        # schedule.every(1).seconds.do(self.run_threaded, self.run_generator_dispatch)
        schedule.every(1).seconds.do(self.run_threaded, self.run_processor_dispatch)
        schedule.every(60).seconds.do(self.run_threaded, self.run_auto_drop_project)
        schedule.every(10).seconds.do(self.run_threaded, self.run_query_project_status)

        while True:
            schedule.run_pending()
            time.sleep(0.5)