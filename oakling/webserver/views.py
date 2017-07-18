#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import datetime

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings

from collector.handler import CollectHandler
from libs.decorator import render_json
from libs.tree.tree import TreeHandler
from libs.tree.tree import ContentsHandler

from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def test_current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body><h2>Welcome to Xspider！ It's Worked! </h2>It is now %s.</body></html>" % (now,)
    return HttpResponse(html)


def home(request):
    """
    home page
    :param request:
    :return:
    """
    return index(request)


def index(request):
    """
    Dashboard Index Page
    :param request:
    :return:
    """
    handler = CollectHandler()
    projects = handler.query_projects_status_by_redis()

    for project in projects:
        if project['total'] >= 0 and project['total'] != project['new']:
            _task_num = float(project['total'] - project['new'])
            project['success_rate'] = round(100 * project['success'] / _task_num, 2)
            project['failed_rate'] = round(100 * project['failed'] / _task_num, 2)
            project['invalid_rate'] = round(100 * project['invalid'] / _task_num, 2)
            project['schedule'] = round((_task_num / project['total']) * 100, 2)
        else:
            project['succ_rate'] = 0
            project['failed_rate'] = 0
            project['invalid_rate'] = 0
            project['schedule'] = 0

        if project['total_d'] >= 0 and project['total_d'] != project['new_d']:
            _task_num = float(project['total_d'] - project['new_d'])
            project['success_rate_d'] = round(100 * project['success_d'] / _task_num, 2)
            project['failed_rate_d'] = round(100 * project['failed_d'] / _task_num, 2)
            project['invalid_rate_d'] = round(100 * project['invalid_d'] / _task_num, 2)
            project['schedule_d'] = round((_task_num / project['total_d']) * 100, 2)
        else:
            project['succ_rate_d'] = 0
            project['failed_rate_d'] = 0
            project['invalid_rate_d'] = 0
            project['schedule_d'] = 0

        if project['total_h'] >= 0 and project['total_h'] != project['new_h']:
            _task_num = float(project['total_h'] - project['new_h'])
            project['success_rate_h'] = round(100 * project['success_h'] / _task_num, 2)
            project['failed_rate_h'] = round(100 * project['failed_h'] / _task_num, 2)
            project['invalid_rate_h'] = round(100 * project['invalid_h'] / _task_num, 2)
            project['schedule_h'] = round((_task_num / project['total_h']) * 100, 2)
        else:
            project['succ_rate_h'] = 0
            project['failed_rate_h'] = 0
            project['invalid_rate_h'] = 0
            project['schedule_h'] = 0

        if project['total_m'] >= 0 and project['total_m'] != project['new_m']:
            _task_num = float(project['total_m'] - project['new_m'])
            project['success_rate_m'] = round(100 * project['success_m'] / _task_num, 2)
            project['failed_rate_m'] = round(100 * project['failed_m'] / _task_num, 2)
            project['invalid_rate_m'] = round(100 * project['invalid_m'] / _task_num, 2)
            project['schedule_m'] = round((_task_num / project['total_m']) * 100, 2)
        else:
            project['succ_rate_m'] = 0
            project['failed_rate_m'] = 0
            project['invalid_rate_m'] = 0
            project['schedule_m'] = 0

    return render_to_response("index.html", {'projects': projects, 'tasks': None, 'profile': None,})


@csrf_exempt
@render_json
def debug(request, name):
    """
    Debug index page
    :param request:
    :return:
    """
    handler = CollectHandler()
    projects = handler.query_projects_status_by_redis(name=name)
    project = projects[0]

    return render_to_response("debug.html", {'project': project})

@csrf_exempt
@render_json
def info(request, name):
    """
    Debug index page
    :param request:
    :return:
    """
    handler = CollectHandler()
    projects = handler.query_projects_status_by_redis(name=name)
    project = projects[0]

    return render_to_response("info.html", {'project': project})

# Unuse, Move to storager.views
# @csrf_exempt
# @render_json
# def data(request):
#     """
#     Data index page
#     :param request:
#     :return:
#     """
#     handler = CollectHandler()
#     projects = handler.query_projects_status_by_redis()
#
#     return render_to_response("data.html", {"projects": projects})
#
# @csrf_exempt
# @render_json
# def local(request, name):
#     """
#     Data local-file index page
#     :param request:
#     :return:
#     """
#     path = name
#     name = name.split("/")[0]
#     tree_handler = TreeHandler("LOCAL")
#
#     if name is not None:
#
#         handler = CollectHandler()
#         projects = handler.query_projects_status_by_redis(name=name)
#
#         localpath = path.strip('/')
#         page_title, breadcrumbs = tree_handler.get_tree(localpath)
#
#         contents_manager = ContentsHandler("LOCAL")
#         result = contents_manager.get(path, request)
#
#         if result["status"] is True and projects:
#             content_models = result["data"]
#             return render_to_response(
#                 "data-local.html", {
#                     "project": projects[0],
#                     "trees": content_models,
#                     "page_title": page_title,
#                     "breadcrumbs": breadcrumbs,
#                     "last_breadcrumbs": breadcrumbs[-2],
#                     "next_breadcrumbs": breadcrumbs[-1],
#                     "local_data_dir": os.path.join(settings.LOCAL_DATAFILE_DIRS, name)
#                 })
#         else:
#             return page_404(request)
#     else:
#         return page_404(request)
#
# @csrf_exempt
# @render_json
# def hdfs(request, name):
#     """
#     Data local-file index page
#     :param request:
#     :return:
#     """
#     path = name
#     name = name.split("/")[0]
#     tree_handler = TreeHandler("HDFS")
#
#     if name is not None:
#
#         handler = CollectHandler()
#         projects = handler.query_projects_status_by_redis(name=name)
#
#         localpath = path.strip('/')
#         page_title, breadcrumbs = tree_handler.get_tree(localpath)
#
#         contents_manager = ContentsHandler("HDFS")
#         result = contents_manager.get(path, request)
#
#         if result["status"] is True and projects:
#             content_models = result["data"]
#             return render_to_response(
#                 "data-hdfs.html", {
#                     "project": projects[0],
#                     "trees": content_models,
#                     "page_title": page_title,
#                     "breadcrumbs": breadcrumbs,
#                     "last_breadcrumbs": breadcrumbs[-2],
#                     "next_breadcrumbs": breadcrumbs[-1],
#                     "local_data_dir": os.path.join(settings.LOCAL_DATAFILE_DIRS, name)
#                 })
#         else:
#             return page_404(request)
#     else:
#         return page_404(request)
#
#
# @csrf_exempt
# @render_json
# def database(request, name):
#     """
#     Result detail index page
#     :param request:
#     :return:
#     """
#     if name is not None:
#         handler = CollectHandler()
#         projects = handler.query_projects_status_by_redis(name=name)
#
#         return render_to_response("result.html", {"project": projects[0]})
#     else:
#         return
#         # todo


@csrf_exempt
@render_json
def task(request, name):
    """
    Task index page
    :param request:
    :return:
    """
    if name is not None:
        handler = CollectHandler()
        projects = handler.query_projects_status_by_redis(name=name)

        return render_to_response("task.html", {"project": projects[0]})
    else:
        return

        #Todo


@csrf_exempt
@render_json
def log(request, name, task_id):
    """
    Task index page
    :param request:
    :return:
    """
    if name is not None:
        handler = CollectHandler()
        task = handler.query_task_by_task_id(name=name, task_id=task_id)

        print task

        return render_to_response("log.html", {"task": task["task"], 'log': task})
    else:
        return

        #Todo


@csrf_exempt
@render_json
def nodes(request):
    """
    API index page
    :param request:
    :return:
    """
    handler = CollectHandler()
    nodes = handler.query_nodes_in_redis(node='--all')
    # return nodes
    return render_to_response("nodes.html", {'nodes': nodes})


@csrf_exempt
@render_json
def node(request, name):
    """
    API index page
    :param request:
    :return:
    """
    # name = request.GET.get('node')
    # print 'node: ', name

    handler = CollectHandler()
    nodes = handler.query_nodes_in_redis(node=name)
    return nodes
    # return render_to_response("nodes.html", {'nodes': nodes})


@csrf_exempt
@render_json
def api(request):
    """
    API index page
    :param request:
    :return:
    """
    return render_to_response("api.html")


def page_403(request):
    message = {
        "code": 403,
        "info": u"这里比较害羞, 不让看了",
        "tips": u"刷新试一下, 万一能访问了呢",
        "poem": [u"世界那么大", u"我也想去看看", u"去看看那", u"色彩斑斓的世界"]
    }

    return render_to_response("error.html", {"message": message})


def page_404(request):
    message = {
        "code": 404,
        "info": u"找不到了",
        "tips": u"刷新试一下, 万一能访问了呢",
        "poem": [u"世界那么大", u"我也想去看看", u"去看看那", u"色彩斑斓的世界"]
    }
    return render_to_response("error.html", {"message": message})


def page_500(request):
    message = {
        "code": 500,
        "info": u"服务器估计睡着了",
        "tips": u"刷新试一下, 万一能访问了呢",
        "poem": [u"世界那么大", u"我也想去看看", u"去看看那", u"色彩斑斓的世界"]
    }
    return render_to_response("error.html", {"message": message})


def test(request):
    """
    Dashboard Index Page
    :param request:
    :return:
    """
    message = {
        "code": 404,
        "info": u"找不到了",
        "tips": u"刷新试一下, 万一能访问了呢",
        "poem": [u"世界那么大", u"我也想去看看", u"去看看那,", u"色彩斑斓的世界"]
    }
    return render_to_response("error.html", {"message": message})

