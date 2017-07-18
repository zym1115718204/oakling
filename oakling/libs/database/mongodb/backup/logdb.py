#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.6.1
from __future__ import unicode_literals

import datetime
from mongoengine import *
# from django.db import models

from projectdb import Project
from taskdb import Task


class Log(Document):
    project = ReferenceField(Project)
    task = ReferenceField(Task)
    url = StringField(max_length=256)
    update_time = DateTimeField(default=datetime.datetime.now)
    result = StringField(max_length=10240)
    meta = {
        "db_alias": "oakling_log",
        "indexes": ["task"]
    }
