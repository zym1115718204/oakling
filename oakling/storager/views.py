#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from libs.decorator import render_json
from libs.tree.tree import TreeHandler
from libs.tree.tree import ContentsHandler
from storager.handler import StorageHandler
from collector.handler import CollectHandler

from webserver.views import page_403, page_404, page_500

# Create your views here.


@csrf_exempt
@render_json
def data(request):
    """
    Data index page
    :param request:
    :return:
    """
    collecthandler = CollectHandler()
    projects = collecthandler.query_projects_status_by_redis()

    storage_handler = StorageHandler()
    datasystems = storage_handler.query_data_systems_status()

    return render_to_response("data.html", {"projects": projects, "datasystems": datasystems})


@csrf_exempt
@render_json
def local(request, name):
    """
    Data local-file index page
    :param request:
    :return:
    """
    path = name
    name = name.split("/")[0]
    tree_handler = TreeHandler("LOCAL")

    if name is not None:

        handler = CollectHandler()
        projects = handler.query_projects_status_by_redis(name=name)

        localpath = path.strip('/')
        page_title, breadcrumbs = tree_handler.get_tree(localpath)

        contents_manager = ContentsHandler("LOCAL")
        result = contents_manager.get(path, request)

        if result["status"] is True and projects:
            content_models = result["data"]
            return render_to_response(
                "data-local.html", {
                    "project": projects[0],
                    "trees": content_models,
                    "page_title": page_title,
                    "breadcrumbs": breadcrumbs,
                    "last_breadcrumbs": breadcrumbs[-2],
                    "next_breadcrumbs": breadcrumbs[-1],
                    "local_data_dir": os.path.join(settings.LOCAL_DATAFILE_DIRS, name)
                })
        else:
            return page_404(request)
    else:
        return page_404(request)


@csrf_exempt
@render_json
def hdfs(request, name):
    """
    Data local-file index page
    :param request:
    :return:
    """
    path = name
    name = name.split("/")[0]
    tree_handler = TreeHandler("HDFS")

    if name is not None:

        handler = CollectHandler()
        projects = handler.query_projects_status_by_redis(name=name)

        localpath = path.strip('/')
        page_title, breadcrumbs = tree_handler.get_tree(localpath)

        contents_manager = ContentsHandler("HDFS")
        result = contents_manager.get(path, request)

        if result["status"] is True and projects:
            content_models = result["data"]
            return render_to_response(
                "data-hdfs.html", {
                    "project": projects[0],
                    "trees": content_models,
                    "page_title": page_title,
                    "breadcrumbs": breadcrumbs,
                    "last_breadcrumbs": breadcrumbs[-2],
                    "next_breadcrumbs": breadcrumbs[-1],
                    "local_data_dir": os.path.join(settings.LOCAL_DATAFILE_DIRS, name)
                })
        else:
            return page_404(request)
    else:
        return page_404(request)


@csrf_exempt
@render_json
def database(request, name):
    """
    Result detail index page
    :param request:
    :return:
    """
    if name is not None:
        handler = CollectHandler()
        projects = handler.query_projects_status_by_redis(name=name)

        return render_to_response("result.html", {"project": projects[0]})
    else:
        return
        # todo

