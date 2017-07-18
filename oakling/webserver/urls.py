#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from webserver import views
from storager import views as storage_views


urlpatterns = [
    # Test views
    url(r'^test$', views.test),
    url(r'^time/$', views.test_current_datetime),

    # Projects views
    url(r'^$', views.index),
    url(r'^debug/(?P<name>\w+)/$', views.debug),
    url(r'^info/(?P<name>\w+)/$', views.info),
    url(r'^task/(?P<name>\w+)/$', views.task),
    url(r'^task/(?P<name>\w+)/(?P<task_id>\w+)/$', views.log),

    # Data views
    url(r'^data/$', storage_views.data),
    url(r'^data/hdfs/(?P<name>.+)/$', storage_views.hdfs),
    url(r'^data/local/(?P<name>.+)/$', storage_views.local),
    url(r'^data/database/(?P<name>\w+)/$', storage_views.database),

    # Node views
    url(r'^nodes/$', views.nodes),
    url(r'^node/(?P<name>.+)$', views.node),

    # API views
    url(r'^api$', views.api),
]
