#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-03-2
# Project: Handler

import os
import time
import json
import redis
import string
import codecs
import datetime
import traceback

from django.conf import settings
from django.utils.encoding import smart_unicode

from libs.database.mongodb.projectdb import Project


class CollectHandler(object):
    """
    Oakling Handler Route Module
    """
    def __init__(self):
        """
        Parameters Initialization
        """
        self._query = Query()
        self._command = Command()

    def query_all_projects_status(self, name="--all"):
        """
        Query Projects Status to Redis
        """
        _projects = self._query.query_projects_by_name(name)
        projects = []
        for project in _projects:
            name = project.name
            group = project.group
            task = "{0}Task".format(str(name).capitalize())
            result = "{0}Result".format(str(name).capitalize())
            now = datetime.datetime.now()
            day = now-datetime.timedelta(days=1)
            hour = now-datetime.timedelta(hours=1)
            minute = now-datetime.timedelta(minutes=1)

            # Notice: Checking
            exec ("from execute.{0}_models import *".format(name))
            exec("total = {0}.objects().count()".format(task))
            exec("new = {0}.objects(status={0}.STATUS_LIVE, ).count()".format(task))
            exec("success = {0}.objects(status={0}.STATUS_SUCCESS).count()".format(task))
            exec("failed = {0}.objects(status={0}.STATUS_FAIL).count()".format(task))
            exec("invalid = {0}.objects(status={0}.STATUS_INVALID).count()".format(task))

            exec ("total_d = {0}.objects(add_time__gte=day).count()".format(task))
            exec ("new_d = {0}.objects(status={0}.STATUS_LIVE, add_time__gte=day).count()".format(task))
            exec ("success_d = {0}.objects(status={0}.STATUS_SUCCESS, add_time__gte=day).count()".format(task))
            exec ("failed_d = {0}.objects(status={0}.STATUS_FAIL, add_time__gte=day).count()".format(task))
            exec ("invalid_d = {0}.objects(status={0}.STATUS_INVALID, add_time__gte=day).count()".format(task))

            exec ("total_h = {0}.objects(add_time__gte=hour).count()".format(task))
            exec ("new_h = {0}.objects(status={0}.STATUS_LIVE, add_time__gte=hour).count()".format(task))
            exec ("success_h = {0}.objects(status={0}.STATUS_SUCCESS, add_time__gte=hour).count()".format(task))
            exec ("failed_h = {0}.objects(status={0}.STATUS_FAIL, add_time__gte=hour).count()".format(task))
            exec ("invalid_h = {0}.objects(status={0}.STATUS_INVALID, add_time__gte=hour).count()".format(task))

            exec ("total_m = {0}.objects(add_time__gte=minute).count()".format(task))
            exec ("new_m = {0}.objects(status={0}.STATUS_LIVE, add_time__gte=minute).count()".format(task))
            exec ("success_m = {0}.objects(status={0}.STATUS_SUCCESS, add_time__gte=minute).count()".format(task))
            exec ("failed_m = {0}.objects(status={0}.STATUS_FAIL, add_time__gte=minute).count()".format(task))
            exec ("invalid_m = {0}.objects(status={0}.STATUS_INVALID, add_time__gte=minute).count()".format(task))

            # exec ("result_total = {0}.objects().count()".format(result))

            # iplimit = project.downloader_interval
            iplimit = 1001
            priority = project.priority
            script = project.script
            models = project.models
            type = project.type
            args = project.args
            interval = project.generator_interval
            speed = project.downloader_dispatch
            # limit = project.downloader_limit
            limit = 1001
            status = project.status
            timeout = project.timeout

            job_dict = {
                'id': str(project.id),
                'name': name,
                'group': group,
                'info': project.info,
                'status': status,
                'priority': priority,
                'type': type,
                'args': args,
                'script': script,
                'models': models,
                'interval': interval,
                'total': total,
                'new': new,
                'success': success,
                'failed': failed,
                'invalid': invalid,
                'total_d': total_d,
                'new_d': new_d,
                'success_d': success_d,
                'failed_d': failed_d,
                'invalid_d': invalid_d,
                'total_h': total_h,
                'new_h': new_h,
                'success_h': success_h,
                'failed_h': failed_h,
                'invalid_h': invalid_h,
                'total_m': total_m,
                'new_m': new_m,
                'success_m': success_m,
                'failed_m': failed_m,
                'invalid_m': invalid_m,
                 # 'result_total': result_total,
                'iplimit': iplimit,
                'speed': speed,
                'limit': limit,
                'timeout': timeout,
                'update_time': project.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                'add_time': project.add_time.strftime("%Y-%m-%d %H:%M:%S"),
                'redis_update': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            projects.append(job_dict)

        # Store Redis
        r = redis.Redis.from_url(settings.ANALYSIS_REDIS)
        for data in projects:
            REDIS_TABLE = "{0}_status".format(data.get("name"))
            r.hset(REDIS_TABLE, data.get("name"), json.dumps(data))

        return projects

    def query_projects_status_by_redis(self, name="--all"):
        """
        Query Projects Status from Redis
         :return:
         data:
        {
            'job_name1':{'id':id,},
            'job_name2':{},
        }
        """
        r = redis.Redis.from_url(settings.ANALYSIS_REDIS)
        _projects = self._query.query_projects_by_name(name)
        projects = []

        for i, project in enumerate(_projects):
            REDIS_TABLE = "{0}_status".format(project.name)
            r_dict = r.hgetall(REDIS_TABLE)

            if r_dict:
                project_status = json.loads(r_dict[project.name])
                total = int(project_status.get('total', "0"))
                new = int(project_status.get('new', "0"))
                success = int(project_status.get('success', "0"))
                failed = int(project_status.get('failed', "0"))
                invalid = int(project_status.get('invalid', "0"))

                total_d = int(project_status.get('total_d', "0"))
                new_d = int(project_status.get('new_d', "0"))
                success_d = int(project_status.get('success_d', "0"))
                failed_d = int(project_status.get('failed_d', "0"))
                invalid_d = int(project_status.get('invalid_d', "0"))

                total_h = int(project_status.get('total_h', "0"))
                new_h = int(project_status.get('new_h', "0"))
                success_h = int(project_status.get('success_h', "0"))
                failed_h = int(project_status.get('failed_h', "0"))
                invalid_h = int(project_status.get('invalid_h', "0"))

                total_m = int(project_status.get('total_m', "0"))
                new_m = int(project_status.get('new_m', "0"))
                success_m = int(project_status.get('success_m', "0"))
                failed_m = int(project_status.get('failed_m', "0"))
                invalid_m = int(project_status.get('invalid_m', "0"))

                result_total = int(project_status.get('result_total', "0"))
                redis_update = str(project_status.get('redis_update', "N/A"))
            else:
                total = 0
                new = 0
                success = 0
                failed = 0
                invalid = 0
                total_d = 0
                new_d = 0
                success_d = 0
                failed_d = 0
                invalid_d = 0
                total_h = 0
                new_h = 0
                success_h = 0
                failed_h = 0
                invalid_h = 0
                total_m = 0
                new_m = 0
                success_m = 0
                failed_m = 0
                invalid_m = 0
                result_total = 0
                redis_update = "N/A"

            job_dict = {
                'index': i%8,
                'id': str(project.id),
                'name': project.name,
                'type': project.type,
                'group': project.group,
                'info': project.info,
                'status': project.status,
                'priority': project.priority,
                'args': project.args,
                'script': project.script,
                'models': project.models,
                'interval': int(project.generator_interval),
                'total': total,
                'new': new,
                'success': success,
                'failed': failed,
                'invalid': invalid,
                'total_d': total_d,
                'new_d': new_d,
                'success_d': success_d,
                'failed_d': failed_d,
                'invalid_d': invalid_d,
                'total_h': total_h,
                'new_h': new_h,
                'success_h': success_h,
                'failed_h': failed_h,
                'invalid_h': invalid_h,
                'total_m': total_m,
                'new_m': new_m,
                'success_m': success_m,
                'failed_m': failed_m,
                'invalid_m': invalid_m,
                'result_total': result_total,
                'speed': int(project.downloader_dispatch),
                 # 'limit': int(project.downloader_limit),
                 # 'iplimit': int(project.downloader_interval),
                'limit': int(60),
                'iplimit': int(1001),
                'timeout': int(project.timeout),
                'update_time': project.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                'add_time': project.add_time.strftime("%Y-%m-%d %H:%M:%S"),
                'redis_update': redis_update,
            }

            projects.append(job_dict)

        return projects

    def query_result_by_name(self, name, page, rows):
        """
        Query result by project name
        :param name:
        :return:
        """
        result = self._query.dump_result_as_json_by_name(name, page, rows)
        return result

    def query_task_by_name(self, name, page, rows):
        """
        Query result by project name
        :param name:
        :return:
        """
        result = self._query.dump_task_as_json_by_name(name, page, rows)
        return result

    def query_task_by_task_id(self, name, task_id):
        """
        Query result by project name
        :param name:
        :return:
        """
        result = self._query.dump_task_as_json_by_task_id(name, task_id)
        return result

    def query_nodes_in_redis(self, node):
        """
        Query nodes in redis
        :return:
        """
        result = self._query.query_nodes_in_redis(node)
        return result

    def edit_project_settings(self, data):
        """
        Edit Project Settings Route
        :param data:
        :return:
        """
        result = self._command.edit_project_settings(data)
        return result

    def create_project(self, project, project_type, args={}, host="http://www.example.com"):
        """
        Create Project Route
        :param project:
        :param host:
        :return:
        """
        result = self._command.create_project(project, project_type, args, host)
        return result

    def query_project(self, project):
        """
        Get Project Route
        :param project:
        :param host:
        :return:
        """
        result = self._query.query_projects_by_name(project)
        return result

    def drop_project(self, project):
        """
        Create Project Route
        :param project:
        :param host:
        :return:
        """
        result = self._command.drop_project(project)
        return result

    def run_once_processor(self, project, channel=None):
        """
        Run Once Project Processor Route
        :param project:
        :return:
        """
        result = self._command.run_once_processor(project, channel)
        return result

    # def run_generator(self, project):
    #     """
    #     Run Project Generator Route
    #     :param project:
    #     :return:
    #     """
    #     result = self._command.run_generator(project)
    #     return result
    #
    # def run_processor(self, project):
    #     """
    #     Run Project Processor Route
    #     :param project:
    #     :return:
    #     """
    #     result = self._command.run_processor(project)
    #     return result


class Query(object):
    """
    Query Handler
    """

    def __init__(self):
        """
        Initialization
        """
        pass

    @staticmethod
    def query_projects_by_name(name):
        """
        Get Projects by Name
        :return: jobs list
        """
        name = smart_unicode(name)
        if not name:
            return
        if name == "--all":
            projects = Project.objects()
        else:
            projects = Project.objects(name=name)

        return projects

    @staticmethod
    def query_result_by_name(name, page, rows):
        """
        Query result by project name
        :return:
        """
        data = []
        total = 0
        result = []
        start = time.time()
        exec("from execute.{0}_models import {1}Result".format(name, name.capitalize()))
        exec("total = {0}Result.objects().count()".format(name.capitalize()))
        exec("data = {0}Result.objects()[((page * rows - 1) // rows) * rows:page * rows]".format(name.capitalize()))

        result_append = result.append
        for _data in data:
            _result = json.loads(_data["result"])
            _result["update_time"] = _data["update_time"].strftime("%Y-%m-%d %H:%M:%S"),
            result_append(_result)

        return {
            "project": name,
            "data": result,
            "total": total,
            "total_page": (total + rows - 1) // rows,
            "page": page,
            "status": True,
            "spend_time": time.time()-start
        }

    @staticmethod
    def query_task_by_name(name, page, rows):
        """
        Query result by project name
        :return:
        """
        data = []
        total = 0
        result = []
        start = time.time()
        exec ("from execute.{0}_models import {1}Task".format(name, name.capitalize()))
        exec ("total = {0}Task.objects().count()".format(name.capitalize()))
        exec ("data = {0}Task.objects().order_by('-add_time')[((page * rows - 1) // rows) * rows:page * rows]".format(name.capitalize()))

        result_append = result.append
        for _data in data:
            result_append({
                "project": str(_data.project.id),
                "status": _data.status,
                "task_id": _data.task_id,
                "update_time": _data.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                "add_time": _data.add_time.strftime("%Y-%m-%d %H:%M:%S"),
                "schedule": _data.schedule,
                # "url": _data.url,
                "url": "https://www.oakling.com",
                "args": _data.args,
                "info": _data.info,
                "retry_times": _data.retry_times,
                "callback": _data.callback,
                "track_log": _data.track_log,
                "spend_time": _data.spend_time,
            })

        return {
            "project": name,
            "task": result,
            "total": total,
            "total_page": (total + rows - 1) // rows,
            "page": page,
            "status": True,
            "spend_time": time.time() - start
        }

    @staticmethod
    def query_task_by_id(name, task_id):
        """
        Query result by project name
        :return:
        """
        start = time.time()
        exec ("from execute.{0}_models import {1}Task".format(name, name.capitalize()))
        exec ("total = {0}Task.objects().count()".format(name.capitalize()))
        exec ('data = {0}Task.objects(task_id="{1}").first()'.format(name.capitalize(), task_id))

        task = {
            "project": str(data.project.id),
            "status": data.status,
            "task_id": data.task_id,
            "update_time": data.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "add_time": data.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            "schedule": data.schedule,
            # "url": data.url,
            "url": "http://www.oakling.com",
            "args": data.args,
            "info": data.info,
            "retry_times": data.retry_times,
            "callback": data.callback,
            "track_log": data.track_log,
            "spend_time": data.spend_time,
        }

        return {
            "project": name,
            "task": task,
            "status": True,
            "spend_time": time.time() - start
        }

    @staticmethod
    def query_nodes_in_redis(node='--all'):
        """
        Query nodes in redis
        :return:
        """
        local = {}
        proxies = {}

        r = redis.Redis.from_url(settings.NODES_REDIS)
        try:
            if node == '--all':
                all_keys = r.hgetall(settings.NODES).keys()
                for key in all_keys:
                    _value = r.hget(settings.NODES, key)
                    value = json.loads(_value)
                    local[key] = value
                all_keys = r.hgetall(settings.PROXIES).keys()
                for key in all_keys:
                    _value = r.hget(settings.PROXIES, key)
                    value = json.loads(_value)
                    proxies[key] = value

                result = {
                    'local': local,
                    'proxies':  proxies,
                    'status': True,
                    'message': 'Success'
                }
            else:
                value = r.hget(settings.NODES, node) or r.hget(settings.PROXIES, node) or '{}'
                result = {
                    'node': {node: json.loads(value)},
                    'stauts': True,
                    'message': 'Success'
                }

            return result


        except Exception:
            reason = traceback.format_exc()
            message = 'Failed to query node %s !, reason: %s' % (node, reason)
            return {
                "status": False,
                "message": message
            }

    def dump_result_as_json_by_name(self, name, page, rows):
        """
        Dump as Json
        :return:
        """
        name = smart_unicode(name)
        project = Project.objects(name=name).first()
        if project:
            result = self.query_result_by_name(name, page, rows)
        else:
            result = None
        return result

    def dump_task_as_json_by_name(self, name, page, rows):
        """
        Dump as Json
        :return:
        """
        name = smart_unicode(name)
        project = Project.objects(name=name).first()
        if project:
            result = self.query_task_by_name(name, page, rows)
        else:
            result = None
        return result

    def dump_task_as_json_by_task_id(self, name, task_id):
        """
        Dump as Json
        :return:
        """
        name = smart_unicode(name)
        project = Project.objects(name=name).first()
        if project:
            result = self.query_task_by_id(name,task_id)
        else:
            result = None
        return result


class Command(object):
    """
    Command Handler
    """
    """
    # Application Information:
    # ---- edit_project_settings
    # ---- create_project
    # -------- start_project
    # -------- load_project
    # ------------ _load_project
    # -------- init_project
    # ---- drop_project
    # -------- _drop_project
    # -------- _drop_execute_path
    # -------- _drop_project_path
    """

    def __init__(self):
        """
        Initialization
        """
        pass

    def edit_project_settings(self, data):
        """
        Edit Project Settings
        :return:
        """

        name = data.get("project").strip()
        project = Project.objects(name=name).first()
        if project is None:
            return {
                "status": False,
                "project": name,
                "message": "Bab Parameters",
                "code": 4002,
            }
        else:
            try:
                if data.get("group", False):
                    project.update(group=str(data.get("group").strip()))
                if data.get("timeout", False):
                    project.update(timeout=int(data.get("timeout").strip()))
                if data.get("status", False):
                    project.update(status=int(data.get("status").strip()))
                if data.get("args", False):
                    project.update(args=str(data.get("args").encode("utf-8").strip()))
                if data.get("priority", False):
                    project.update(priority=int(data.get("priority").strip()))
                if data.get("info", False):
                    project.update(info=data.get("info").strip())
                if data.get("script", False):
                    project.update(script=str(data.get("script".strip().decode('utf-8'))))
                if data.get("interval", False):
                    project.update(generator_interval=str(int(data.get("interval").strip())))
                if data.get("ip_limit", False):
                    project.update(downloader_interval=str(int(data.get("ip_limit").strip())))
                if data.get("limit", False):
                    project.update(downloader_limit=str(int(data.get("limit").strip())))
                if data.get("number", False):
                    project.update(downloader_dispatch=int(data.get("number").strip()))

                project.update(update_time=datetime.datetime.now())

            except ValueError:
                return {
                    "status": False,
                    "project": name,
                    "message": "Bad Parameters",
                    "reason": traceback.format_exc(),
                    "code": 4003,
                }
            except Exception:
                return {
                    "status": False,
                    "project": name,
                    "message": "Internal Server Error",
                    "code": 5001
                }

        return {
            "status": True,
            "project": name,
            "message": "Operation Succeeded",
            "code": 2001
        }

    def create_project(self, project_name, project_type, args, host="http://www.example.com"):
        """
        Create Project
        :return:
        """
        project_type = project_type.strip().lower()
        project_name = project_name.strip().lower()
        result = self.start_project(project_name, project_type, host)
        if result["status"] is True:
            if not args:
                args = json.dumps({"_project_name": project_name})
            result = self.load_project(project_name, project_type, args)
            if result['status'] is True:
                result = self.init_project(project_name)
                return result
            else:
                return result
        else:
            return result

    @staticmethod
    def start_project(project_name, project_type, host="http://www.example.com"):
        """
        Start Project
        :return:
        """
        # Todo settings.database
        database = "mongodb"

        try:
            _projectname = project_name.lower()
            _project_type = project_type.strip().lower()
            project_path = os.path.join(settings.PROJECTS_PATH, _projectname)

            if not os.path.exists(project_path):
                os.makedirs(project_path)

            tmpl_path = os.path.join(settings.BASE_DIR, 'libs', 'basetemplate', '{0}.tmpl'.format(_project_type))
            with open(tmpl_path, 'rb') as fp:
                raw = fp.read().decode('utf8')
            create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            content = string.Template(raw).substitute(CREATE_TIME=create_time,
                                                      PROJECTS_NAME=_projectname,
                                                      START_URL=host)

            spider_path = os.path.join(project_path, '%s_spider.py' % (_projectname))
            if not os.path.exists(spider_path):
                with open(spider_path, 'w') as fp:
                    fp.write(content.encode('utf8'))

                message = 'Successfully create a new project %s !' % (_projectname)
                # print message
            else:
                message = 'Failed to create project %s , Project already exists! ' % (_projectname)
                return {
                    "status": False,
                    "message": message
                }

            tmpl_path = os.path.join(settings.BASE_DIR, 'libs', 'database', database, 'models.tmpl')
            with open(tmpl_path, 'rb') as fp:
                raw = fp.read().decode('utf8')
            create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            content = string.Template(raw).substitute(CREATE_TIME=create_time,
                                                      PROJECTS_NAME=_projectname,
                                                      PROJECTS_NAME_TASK=str(_projectname).capitalize() + 'Task',
                                                      PROJECTS_NAME_RESULT=str(
                                                          _projectname).capitalize() + 'Result')

            models_path = os.path.join(project_path, '%s_models.py' % (_projectname))
            if not os.path.exists(models_path):
                with open(models_path, 'w') as fp:
                    fp.write(content.encode('utf8'))
                message = 'Successfully create a new project models %s !' % (models_path)

                return {
                    "status": True,
                    "message": message
                }
            else:
                message = 'Failed to create project %s , Project already exists! ' % (models_path)
                return {
                    "status": False,
                    "message": message
                }

        except Exception:
            reason = traceback.format_exc()
            message = 'Failed to create new project %s !, reason: %s' % (project_name, reason)
            return {
                "status": False,
                "message": message
            }

    def load_project(self, project_name, project_type, args):
        """
        Load Project
        :return:
        """
        try:
            project_path = os.path.join(settings.PROJECTS_PATH, project_name)
            if not os.path.exists(project_path):
                os.makedirs(project_path)

            spider_path = os.path.join(project_path, '%s_spider.py' % (project_name))
            models_path = os.path.join(project_path, '%s_models.py' % (project_name))
            if not os.path.exists(spider_path) or not os.path.exists(models_path):
                message = 'Failed to load project %s , Project does not exist! ' % (project_name)
                return {
                    "status": False,
                    "message": message
                }
            else:
                result = self._load_project(project_name, project_type, spider_path, models_path, args)
                return result

        except Exception:
            reason = traceback.format_exc()
            message = ('Failed to create new project %s !, Reason: %s' % (project_name, reason))

            return {
                "status": False,
                "message": message
            }

    @staticmethod
    def _load_project(project_name, project_type, spider_path, models_path, args):
        """
        _load project
        :param project_name:
        :param spider_path:
        :param models_path:
        :return:
        """
        try:
            with open(spider_path, 'rb') as fp:
                spider_script = fp.read().decode('utf8')
            with open(models_path, 'rb') as fp:
                models_script = fp.read().decode('utf8')
            project = Project.objects(name=project_name).first()
            if project:
                project.update(script=spider_script)
                project.update(models=models_script)
            else:
                project = Project(name=project_name,
                                  info="",
                                  type=project_type,
                                  args=args,
                                  script=spider_script,
                                  models=models_script,
                                  generator_interval="60",
                                  # downloader_interval="60",
                                  downloader_dispatch=1)
                project.save()
            message = 'Successfully load project %s !' % (project_name)
            return {
                "status": True,
                "message": message
            }

        except Exception:
            reason = traceback.format_exc()
            message = 'Failed to load project %s !, Reason: %s' % (spider_path, reason)
            return {
                "status": False,
                "message": message
            }

    @staticmethod
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
            _spider_path = os.path.join(settings.EXECUTE_PATH, "%s_spider.py" %(project_name))
            _models_path = os.path.join(settings.EXECUTE_PATH, "%s_models.py" %(project_name))
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

    def drop_project(self, project_name):
        """
        Drop Project
        # Delete PROJECT ==> Delete EXECUTE PATH ==> Delete PROJECT PATH,
        # Not Delete PROJECT TASK
        :return:
        """

        project_name = project_name.strip().lower()
        result = self._drop_project(project_name)
        if result["status"] is True:
            result = self._drop_execute_path(project_name)
            if result['status'] is True:
                result = self._drop_project_path(project_name)
                return result
            else:
                return result
        else:
            return result

        # try:
        #     .....
        #
        # except Exception:
        #     reason = traceback.format_exc()
        #     message = ('Failed to drop project %s !, Reason: %s' % (project_name, reason))
        #
        #     return {
        #         "status": False,
        #         "reason": reason,
        #         "message": message
        #     }

    @staticmethod
    def _drop_project(project_name):
        """
        Delete project task from database

        Note: When MongoEngineConnectionError:alias "oakling_project" has not been defined
              Must Use settings.Para  to activate settings
        :return:
        """
        activate = settings.BASE_DIR

        try:
            project = Project.objects(name=project_name).first()

            if project:
                exec ("from execute.{0}_models import *".format(project_name))
                exec ("{0}{1}.objects(project=project).delete()".format(str(project_name).capitalize(), "Task"))
                project.delete()
                # project.save()
                message = 'Successfully delete project from database %s !' % (project_name)
            else:
                message = 'project is not exist on database %s !' % (project_name)

            return {
                "status": True,
                "message": message
            }

        except Exception:
            reason = traceback.format_exc()
            message = ('Failed to delete project from database %s !, Reason: %s' % (project_name, reason))

            return {
                "status": False,
                "message": message
            }

    @staticmethod
    def _drop_execute_path(project_name):
        """
        Delete project from execute path
        :return:
        """
        try:
            if not os.path.exists(settings.EXECUTE_PATH):
                message = "Execute path is not exist."
                return {
                    "status": True,
                    "message": message
                }
            _spider_path = os.path.join(settings.EXECUTE_PATH, "%s_spider.py" % (project_name))
            _models_path = os.path.join(settings.EXECUTE_PATH, "%s_models.py" % (project_name))

            for path in (_models_path, _spider_path):
                if os.path.exists(path):
                    os.remove(path)

            message = 'Successfully delete project from execute path %s !' % (project_name)
            return {
                "status": True,
                "message": message
            }

        except Exception:
            reason = traceback.format_exc()
            message = ('Failed to delete project from execute path %s !, Reason: %s' % (project_name, reason))

            return {
                "status": False,
                "message": message
            }

    @staticmethod
    def _drop_project_path(project_name):
        """
        Delete project from project path
        :return:
        """
        try:
            if not os.path.exists(settings.PROJECTS_PATH):
                message = "Project path is not exist."
                return {
                    "status": True,
                    "message": reason
                }

            _project_path = os.path.join(settings.PROJECTS_PATH, project_name)
            if os.path.exists(_project_path):
                # Use shutil package remove file and dir
                __import__('shutil').rmtree(_project_path)

            message = 'Successfully delete project from project path %s !' % (project_name)
            return {
                "status": True,
                "message": message
            }

        except Exception:
            reason = traceback.format_exc()
            message = ('Failed to delete project from project path %s !, Reason: %s' % (project_name, reason))

            return {
                "status": False,
                "message": message
            }

    @staticmethod
    def run_once_processor(project_name, channel=None, **kw):
        """
        Run Once Processor
        :return:
        """
        try:
            activate = settings.BASE_DIR

            from collector.utils import OnceProcessor

            once_processor = OnceProcessor()

            project_name = project_name.strip().lower()
            project = Project.objects(name=project_name).first()

            # Todo
            # config_args should import from project db

            config_args = {
                "num": 10,
                "output_path": "/tmp/nginx-test.log",
                "command": "ls -ll "
            }


            config_args = {}

            if project:
                result = once_processor.run_processor(project_name, channel, **config_args)
            else:
                message = 'Project %s does not exist!' % (project_name)
                result = {
                    "status": False,
                    "message": message
                }
            message = 'Successfully run processor %s !' % (project_name)
            return {
                "status": True,
                "message": message,
                "task": result
            }

        except Exception:
            reason = traceback.format_exc()
            message = ('Failed to run once project from project path %s !, Reason: %s' % (project_name, reason))

            return {
                "status": False,
                "message": message
            }

    # def run_generator(self, project_name):
    #     """
    #     Create Project
    #     :return:
    #     """
    #     try:
    #         project_name = project_name.strip()
    #         project = Project.objects(name=project_name).first()
    #         if project is None:
    #             message = 'Project %s does not exist!' % (project_name)
    #             return {
    #                 "status": False,
    #                 "message": message
    #             }
    #         if project.status != 2:
    #             message = 'Project %s status is not Debug, please set status to DEBUG.' % (project_name)
    #             return {
    #                 "status": False,
    #                 "message": message
    #             }
    #         else:
    #             from collector.utils import Generator
    #             project_id = str(project.id)
    #             generator = Generator(project_id)
    #             task = generator.run_generator()
    #
    #             # processor = Processor(task=task["result"])
    #             # result = processor.run_processor()
    #             # print result
    #
    #             message = 'Successfully run project %s !' % (project_name)
    #             return {
    #                 "status": True,
    #                 "message": message,
    #                 "task": task
    #             }
    #
    #     except Exception:
    #         reason = traceback.format_exc()
    #         message = 'Failed to run project %s !, Reason: %s' % (project_name, reason)
    #         return {
    #             "status": False,
    #             "message": message
    #         }

    # def run_processor(self, project_name, **kw):
    #     """
    #     Create Project
    #     :return:
    #     """
    #     try:
    #         project_name = project_name.strip()
    #         project = Project.objects(name=project_name).first()
    #         if project is None:
    #             message = 'Project %s does not exist!' % (project_name)
    #             return {
    #                 "status": False,
    #                 "message": message
    #             }
    #         if project.status != 2:
    #             message = 'Project %s status is not Debug, please set status to DEBUG.' % (project_name)
    #             return {
    #                 "status": False,
    #                 "message": message
    #             }
    #         else:
    #             from collector.utils import OnceProcessor
    #             processor = OnceProcessor()
    #             result = processor.run_processor(project_name, **kw)
    #
    #             # processor = Processor(task=task["result"])
    #             # result = processor.run_processor()
    #             # print result
    #
    #             message = 'Successfully run processor %s !' % (project_name)
    #             return {
    #                 "status": True,
    #                 "message": message,
    #                 "task": result
    #             }
    #
    #     except Exception:
    #         reason = traceback.format_exc()
    #         message = 'Failed to run project %s !, Reason: %s' % (project_name, reason)
    #         return {
    #             "status": False,
    #             "message": message
    #         }
