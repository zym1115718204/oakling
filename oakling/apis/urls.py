#!/usr/bin/env python
# -*- coding: utf-8 -*-


from . import command
from django.conf.urls import url, include

api_patterns = [
    url(r'^edit$', command.edit_project),
    url(r'^run$', command.run_project),
    url(r'^create$', command.create_project),
    url(r'^task$', command.task_project),
    url(r'^result$', command.result_project),
    url(r'^status$', command.status_project),
]

urlpatterns = [
    url(r'^v1/command/', include(api_patterns)),
]


