#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.6.1
from __future__ import unicode_literals

import datetime
from mongoengine import *
# from django.db import models

from projectdb import Project

class Task(Document):
    (STATUS_LIVE, STATUS_DISPATCH, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS, STATUS_INVALID) = range(0, 6)
    STATUS_CHOICES = ((STATUS_LIVE, u"LIVE"),
                      (STATUS_DISPATCH, u'DISPATCH'),
                      (STATUS_PROCESS, u"PROCESS"),
                      (STATUS_FAIL, u"FAIL"),
                      (STATUS_SUCCESS, u"SUCCESS"),
                      (STATUS_INVALID, u"INVALID"),)

    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    status = IntField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    task_id = StringField(max_length=120)
    update_time = DateTimeField(default=datetime.datetime.now)
    add_time = DateTimeField(default=datetime.datetime.now)
    schedule = StringField(max_length=1024)
    url = StringField(max_length=8000)
    args = StringField(max_length=2048, null=True)
    info = StringField(max_length=2048, null=True)
    retry_times = IntField(default=0)
    callback = StringField(max_length=120)
    track_log = StringField(max_length=10240)
    spend_time = StringField(max_length=120, default='0')
    meta = {
        "allow_inheritance": True,
        "db_alias": "oakling_task",
        "indexes": ["task_id", "url", "status"],
    }

