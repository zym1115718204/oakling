#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.5.21
# Author: Oakling Group

"""
Oakling Collector Utils

"""

import os
import re
import json
import psutil
import socket
import hashlib
import traceback

import time
import uuid
import arrow
import random
import datetime

from faker import Factory
from django.conf import settings

from libs.database.mongodb.projectdb import Project



class InitSpider(object):
    """
    Load Spider Script to Local File
    """

    def __init__(self):
        """
        LoadSpider Initialization
        """
        if not os.path.exists(settings.EXECUTE_PATH):
            os.mkdir(settings.EXECUTE_PATH)

    def load_spider(self, project):
        """
        Load Spider from  Database by project
        :param project:
        :return:
        """
        try:
            project_name = project.name
            spider_script = project.script
            models_script = project.models
            _spider_path = os.path.join(settings.EXECUTE_PATH, "%s_spider.py" %(project_name))
            _models_path = os.path.join(settings.EXECUTE_PATH, "%s_models.py" %(project_name))
            execute_init = os.path.join(settings.EXECUTE_PATH, "__init__.py")

            with open(execute_init, 'w') as fp:
                fp.write("")
            with open(_spider_path, 'w') as fp:
                fp.write(spider_script.encode('utf8'))
            with open(_models_path, 'w') as fp:
                fp.write(models_script.encode('utf8'))

        except Exception:
            print traceback.format_exc()


def init_project(project_name):
    """
    Initialization Project to execute path
    :return:
    """
    if not os.path.exists(settings.EXECUTE_PATH):
        os.mkdir(settings.EXECUTE_PATH)
    project = Project.objects(name=project_name).first()

    try:
        project_name = project.name
        spider_script = project.script
        models_script = project.models
        _spider_path = os.path.join(settings.EXECUTE_PATH, "%s_spider.py" % (project_name))
        _models_path = os.path.join(settings.EXECUTE_PATH, "%s_models.py" % (project_name))
        execute_init = os.path.join(settings.EXECUTE_PATH, "__init__.py")

        with open(execute_init, 'w') as fp:
            fp.write("")
        with open(_spider_path, 'w') as fp:
            fp.write(spider_script.encode('utf8'))
        with open(_models_path, 'w') as fp:
            fp.write(models_script.encode('utf8'))

        message = 'Successfully init project %s !' % (project_name)
        return {
            "status": True,
            "message": message
        }

    except Exception:
        reason = traceback.format_exc()
        message = 'Failed to Init project %s !, Reason: %s' % (project_name, reason)
        return {
            "status": False,
            "message": message
        }






class DemoSpider(object):
    """
    Spider Demo
    """
    @staticmethod
    def generator_nginx_log():
        """
        Generate Nginx Log
        :return:
        """
        fake = Factory.create('it_IT')
        ip = fake.ipv4()

        now_time = datetime.datetime.now()
        user_agent = fake.user_agent()
        city = fake.city_suffix()
        code = random.choice((200, 500, 400))

        return '{0} - - [{1}] "GET HTTP/1.1" {2} "{3}" {4} \n'.format(
            ip, now_time, code, user_agent, city
        )

    def generator_nginx_log_by_num(self, num=1):
        """
        Generate Nginx Log by Number Parameter
        :param num: Integer
        :return:
        """
        nginx_log = ""
        for i in range(0, num):
            log = self.generator_nginx_log()
            nginx_log = "".join((nginx_log, log))

        return nginx_log

    @staticmethod
    def save_to_file(content, output_path="/tmp/nginx-test.log"):
        """
        Save Nginx Log to Path
        :param content:
        :param output_path:
        :return:
        """
        time.sleep(2)
        with open(output_path, 'a') as f:
            f.write(content)

        return{
            "status": True
        }

    def run(self, **kw):
        """
        Run Spider
        :return:
        """
        num = kw.get("num")
        output_path = kw.get("output_path")

        result = self.generator_nginx_log_by_num(num)
        status = self.save_to_file(result, output_path)

        return status


class DemoShell(object):
    """
    Spider Demo
    """
    @staticmethod
    def execute_shell(command):
        """
        Execute shell command
        :return:
        """
        import subprocess

        child = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        child.wait()
        output = child.communicate()
        log = output[0].split("\n")
        for i in log:
            print i

        return {
            "status": True,
            "output": output
        }

    def run(self, **kw):
        """
        Run Spider
        :return:
        """
        num = kw.get("command")
        result = self.execute_shell(num)

        return result


class OnceProcessor(object):
    """
     Processor Module
    """
    def __init__(self, project_name="demoo", _id=None, project_id=None):
        """
        Processor Module Initialization
        :param Json
        """
        # exec ("from execute.{0}_spider import *".format(project_name))
        # self.demo = Spider()
        pass

    def init_project(self):
        """
        Initialization Project to execute path
        :return:
        """
        if not os.path.exists(settings.EXECUTE_PATH):
            os.mkdir(settings.EXECUTE_PATH)
        # project = Project.objects(name=project_name).first()

        try:
            project_name = self.project.name
            spider_script = self.project.script
            models_script = self.project.models
            _spider_path = os.path.join(settings.EXECUTE_PATH, "%s_spider.py" % (project_name))
            _models_path = os.path.join(settings.EXECUTE_PATH, "%s_models.py" % (project_name))
            execute_init = os.path.join(settings.EXECUTE_PATH, "__init__.py")

            with open(execute_init, 'w') as fp:
                fp.write("")
            with open(_spider_path, 'w') as fp:
                fp.write(spider_script.encode('utf8'))
            with open(_models_path, 'w') as fp:
                fp.write(models_script.encode('utf8'))

            message = 'Successfully init project %s !' % (project_name)
            return {
                "status": True,
                "message": message
            }

        except Exception:
            reason = traceback.format_exc()
            message = 'Failed to Init project %s !, Reason: %s' % (project_name, reason)
            return {
                "status": False,
                "message": message
            }

    def init_local_data(self):
        """
        Initialization project local data directory
        :return:
        """
        if not os.path.exists(settings.LOCAL_DATAFILE_DIRS):
            os.mkdir(settings.LOCAL_DATAFILE_DIRS)
        # project = Project.objects(name=project_name).first()

        try:
            project_name = self.project.name
            storage_type = "LOCAL"   # todo
            if storage_type == "LOCAL":
                local_path = os.path.join(settings.LOCAL_DATAFILE_DIRS, "%s" % (project_name))
                if not os.path.exists(local_path):
                    os.mkdir(local_path)

            message = 'Successfully init project data path %s !' % (project_name)
            return {
                "status": True,
                "message": message
            }

        except Exception:
            reason = traceback.format_exc()
            message = 'Failed to Init project  data path %s !, Reason: %s' % (project_name, reason)
            return {
                "status": False,
                "message": message
            }


    def process_task(self, **kw):
        """
        Downloader Module
        :return: Result Dict
        """
        default_retry_times = 0
        try:
            start_time = arrow.now()
            output_result = self.demo.run(**kw)
            end_time = arrow.now()
            spend_time = end_time.float_timestamp - start_time.float_timestamp

            if output_result.get("status") is True:
                return {
                    "status": True,
                    "start_time": str(start_time),
                    "end_time": str(end_time),
                    "spend_time": spend_time,
                    "retry_times": default_retry_times,
                    "track_log": "Success"
                }
            else:
                return {
                    "status": False,
                    "start_time": str(start_time),
                    "end_time": str(end_time),
                    "spend_time": spend_time,
                    "retry_times": default_retry_times,
                    "trace_log": "Failed, reason: {0}".format(output_result)
                }
        except Exception:
            end_time = arrow.now()
            spend_time = end_time.float_timestamp - start_time.float_timestamp
            reason = traceback.format_exc()
            return {
                "status": False,
                "start_time": str(start_time),
                "end_time": str(end_time),
                "spend_time": spend_time,
                "retry_times": default_retry_times,
                "trace_log": "Failed, reason: {0}".format(reason)
            }

    def run_processor(self, project_name, channel=None,  **kw):
        """
        :return:
        """
        # exec ("from execute.{0}_spider import *".format(project_name))
        # self.demo = Spider()

        project_name = project_name.strip().lower()
        self.project = Project.objects(name=project_name).first()

        self.init_project()
        self.init_local_data()

        _spider = __import__("execute.{0}_spider".format(project_name), fromlist=["*"])

        reload(_spider)
        self.demo = _spider.Spider(channel)

        if kw:
            args = kw
        else:
            args = json.loads(self.project.args)

        print "[ INFO DEBUG:]", args

        result = self.process_task(**args)
        return result


class Processor(object):
    """
     Processor Module
    """

    def __init__(self, project_name=None, worker=None):
        """
        Processor Module Initialization
        :param Json
        """
        pass

    def init_project(self):
        """
        Initialization Project to execute path
        :return:
        """
        if not os.path.exists(settings.EXECUTE_PATH):
            os.mkdir(settings.EXECUTE_PATH)
        # project = Project.objects(name=project_name).first()

        try:
            project_name = self.project.name
            spider_script = self.project.script
            models_script = self.project.models
            _spider_path = os.path.join(settings.EXECUTE_PATH, "%s_spider.py" % (project_name))
            _models_path = os.path.join(settings.EXECUTE_PATH, "%s_models.py" % (project_name))
            execute_init = os.path.join(settings.EXECUTE_PATH, "__init__.py")

            with open(execute_init, 'w') as fp:
                fp.write("")
            with open(_spider_path, 'w') as fp:
                fp.write(spider_script.encode('utf8'))
            with open(_models_path, 'w') as fp:
                fp.write(models_script.encode('utf8'))

            message = 'Successfully init project %s !' % (project_name)
            return {
                "status": True,
                "message": message
            }

        except Exception:
            reason = traceback.format_exc()
            message = 'Failed to Init project %s !, Reason: %s' % (project_name, reason)
            return {
                "status": False,
                "message": message
            }

    def init_local_data(self):
        """
        Initialization project local data directory
        :return:
        """
        if not os.path.exists(settings.LOCAL_DATAFILE_DIRS):
            os.mkdir(settings.LOCAL_DATAFILE_DIRS)
        # project = Project.objects(name=project_name).first()

        try:
            project_name = self.project.name
            storage_type = "LOCAL"   # todo
            if storage_type == "LOCAL":
                local_path = os.path.join(settings.LOCAL_DATAFILE_DIRS, "%s" % (project_name))
                if not os.path.exists(local_path):
                    os.mkdir(local_path)

            message = 'Successfully init project data path %s !' % (project_name)
            return {
                "status": True,
                "message": message
            }

        except Exception:
            reason = traceback.format_exc()
            message = 'Failed to Init project  data path %s !, Reason: %s' % (project_name, reason)
            return {
                "status": False,
                "message": message
            }


    def process_task(self, **kw):
        """
        Downloader Module
        :return: Result Dict
        """
        task_status_fail = 3
        task_status_success = 4
        default_retry_times = 0
        start_time = arrow.now()

        try:
            start_time = arrow.now()
            output_result = self.spider.run(**kw)
            end_time = arrow.now()
            spend_time = end_time.float_timestamp - start_time.float_timestamp

            if output_result.get("status") is True:
                return {
                    "status": True,
                    "start_time": str(start_time),
                    "task_status": task_status_success,
                    "end_time": str(end_time),
                    "spend_time": spend_time,
                    "retry_times": default_retry_times,
                    "track_log": "Success"
                }
            else:
                return {
                    "status": False,
                    "start_time": str(start_time),
                    "task_status": task_status_fail,
                    "end_time": str(end_time),
                    "spend_time": spend_time,
                    "retry_times": default_retry_times,
                    "track_log": "Failed, reason: {0}".format(output_result)
                }
        except Exception:
            end_time = arrow.now()
            spend_time = end_time.float_timestamp - start_time.float_timestamp
            reason = traceback.format_exc()

            return {
                "status": False,
                "task_status": task_status_fail,
                "start_time": str(start_time),
                "end_time": str(end_time),
                "spend_time": spend_time,
                "retry_times": default_retry_times,
                "track_log": "Failed, reason: {0}".format(reason)
            }

    def run_processor(self, project_name, **kw):
        """
        :return:
        """
        # exec ("from execute.{0}_spider import *".format(project_name))
        # self.spider = Spider()

        project_name = project_name.strip().lower()
        self.project = Project.objects(name=project_name).first()

        self.init_project()
        self.init_local_data()

        _spider = __import__("execute.{0}_spider".format(project_name), fromlist=["*"])
        reload(_spider)

        self.spider = _spider.Spider()
        self.storage = Storage(project_name)

        result = self.storage.create_task()
        if result["status"] is True:
            # task = result.get("task")
            task_id = result.get("task_id")
            if kw:
                args = kw
            else:
                args = json.loads(result.get("args"))

            result = self.process_task(**args)

            # Todo double data Streaming

            result = self.storage.update_task(
                # task=task,
                task_id=task_id,
                status=result["task_status"],
                track_log=result["track_log"],
                spend_time=result["spend_time"]
            )
            if result.get("status") is True:
                message = 'Successfully run processor %s !' % (project_name)
                result = {
                    "status": True,
                    "message": message
                }
            else:
                reason = result.get("message")
                message = 'Failed run processor %s ,reason: %s!' % (project_name, reason)
                result = {
                    "status": False,
                    "message": message
                }
        else:
            message = result["message"]
            result = {
                "status": False,
                "message": "Failed to run processor, reason:  %s !" % (message)
            }

        return result


class Storage(object):
    """
    Storage Module
    """

    def __init__(self, project_name):
        """
        Initialization
        """
        project_name = project_name.strip().lower()
        self.project = Project.objects(name=project_name).first()

    def create_task(self):
        """
        Store project task
        :return:
        """
        try:
            _status = self.project.status

            if _status == 1:
                name = self.project.name
                args = self.project.args
                task_id = self.str2md5(uuid.uuid4().get_hex())
                generator_interval = self.project.generator_interval

                exec ("from execute.{0}_models import *".format(self.project.name))
                exec ("task = {0}{1}()".format(str(self.project.name).capitalize(), "Task"))
                task.project = self.project
                task.args = args
                task.callback = None
                task.schedule = generator_interval
                task.task_id = task_id
                task.status = 0

                task.save()

                return {
                    "status": True,
                    "message": "success",
                    "task_id": task_id,
                    "args": args
                    # "task": task
                }
            else:
                return {
                    "status": False,
                    "message": "Failed to create task, reason: Project status must be Online"
                }

        except Exception:
            reason = traceback.format_exc()
            message = "Failed to create task, reason: {0}".format(reason)
            return {
                "status": False,
                "message": message
            }

    def update_task(self, task_id, status, track_log, spend_time, retry_times=0):
        """
        Update Task
        :return:
        """
        try:
            _status = self.project.status
            exec ("from execute.{0}_models import *".format(self.project.name))
            exec ("task = {0}{1}.objects(task_id=task_id).first()".format(str(self.project.name).capitalize(), "Task"))

            if _status == 1:
                task.update(
                    status=status,
                    track_log=track_log,
                    update_time=datetime.datetime.now(),
                    spend_time=str(spend_time),
                    retry_times=retry_times,
                )
                return {
                    "status": True,
                    "message": "Success"
                }

            else:
                return {
                    "status": False,
                    "message": "Failed to create task, reason: Project status must be Online"
                }
        except Exception:
            reason = traceback.format_exc()
            message = "Failed to update task, reason: {0}".format(reason)
            return {
                "status": False,
                "message": message
            }


    # def store_task(self, url_dict):
    #     """
    #     Store project task
    #     :return:
    #     """
    #     try:
    #         _status = self.project.status
    #         if _status == 1:
    #
    #             # Save Task to Database
    #             url = url_dict.get("url")
    #             args = url_dict.get("args")
    #             callback = url_dict.get("callback")
    #             task_id = self.str2md5(url_dict.get("url"))
    #
    #             repeat = None
    #             task_object = None
    #             exec ("from execute.{0}_models import *".format(self.project.name))
    #             exec("repeat = {0}{1}.objects(task_id=task_id).first()".format(str(self.project.name).capitalize(), "Task"))
    #
    #             if repeat:
    #                 return{
    #                     "status": True,
    #                     "store_task": False,
    #                     "repeat": True,
    #                 }
    #             else:
    #                 exec ("task_object = {0}{1}()".format(str(self.project.name).capitalize(), "Task"))
    #                 task_object.project = self.project
    #                 task_object.args = json.dumps(args)
    #                 task_object.callback = callback
    #                 task_object.task_id = task_id
    #                 task_object.status = 0
    #                 task_object.url = url
    #
    #                 task_object.save()
    #
    #                 return {
    #                     "status": True,
    #                     "message": ""
    #                 }
    #         else:
    #             return {
    #                 "status": False,
    #                 "message": "Failed to store task, reason: Project status must be Online"
    #             }
    #
    #     except Exception:
    #         reason = traceback.format_exc()
    #         message = "Failed to store task, reason: {0}".format(reason)
    #         return {
    #             "status": False,
    #             "message": message
    #         }

    # def package_task(self, task=None, _id=None):
    #     """
    #     Package Task
    #     :return:
    #     """
    #     _name = self.project.name
    #     _status = self.project.status
    #
    #     if _status == 1:
    #         exec ("from execute.{0}_models import *".format(_name))
    #         exec ('self.task = {0}Task.objects(id="{1}").first()'.format(str(_name).capitalize(), _id))
    #         return self.task
    #
    #     elif _status == 2:
    #         task_object = None
    #         exec ("from execute.{0}_models import *".format(_name))
    #         exec ("task_object = {0}{1}()".format(str(_name).capitalize(), "Task"))
    #
    #         args = task.get("args")
    #         url = task.get("url")
    #         callback = task.get("callback")
    #         task_id = self.str2md5(task.get("url"))
    #
    #         task_object.project = self.project
    #         task_object.task_id = task_id
    #         task_object.callback = callback
    #         task_object.args = json.dumps(args)
    #         task_object.status = 0
    #         task_object.url = url
    #         self.task = task_object
    #
    #         return self.task
    #     else:
    #         raise TypeError("Project Status Must Be Run or Debug.")



    # def store_result(self, result):
    #     """
    #     Store Result
    #     :return:
    #     """
    #     _status = self.project.status
    #     if _status == 1:
    #         # Save Task Result to Database
    #         task_result = None
    #         exec ("from execute.{0}_models import *".format(self.project.name))
    #         exec ("task_result = {0}{1}()".format(str(self.project.name).capitalize(), "Result"))
    #
    #         task_result.project = self.project
    #         task_result.task = self.task
    #         task_result.url = self.task.url
    #         task_result.update_time = datetime.datetime.now()
    #         task_result.result = json.dumps(result)
    #         task_result.save()
    #
    #         return {
    #             "store_result": True
    #         }
    #
    #     elif _status == 2:
    #
    #         task_result = {}
    #         task_result["project"] = str(self.project.id)
    #         task_result["url"] = self.task.url
    #         task_result["update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #         task_result["result"] = result
    #
    #         return task_result
    #     else:
    #         raise TypeError("Project Status Must Be On or Debug.")

    @staticmethod
    def str2md5(string):
        """
        Convert Str to MD5
        :return:
        """
        md5 = hashlib.md5()
        md5.update(string.encode('utf8'))

        return md5.hexdigest()

