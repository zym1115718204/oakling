#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.6.1
from __future__ import unicode_literals

import datetime
from mongoengine import *
# from django.db import models


# Create your models here.
class Project(Document):
    (STATUS_OFF, STATUS_ON, STATUS_DEBUG, STATUS_DELAY) = range(0, 4)
    STATUS_CHOICES = ((STATUS_OFF, "OFFLINE"), (STATUS_ON, u"ONLINE"), (STATUS_DEBUG, u'DEBUG'), (STATUS_DELAY, u'DELAY'))
    (PRIOR_0, PRIOR_1, PRIOR_2, PRIOR_3, PRIOR_4, PRIOR_5, PRIOR_6) = range(-1, 6)
    PRIOR_CHOICES = ((PRIOR_0, u"-1"),
                     (PRIOR_1, u"0"),
                     (PRIOR_2, u"1"),
                     (PRIOR_3, u"2"),
                     (PRIOR_4, u"3"),
                     (PRIOR_5, u"4"),
                     (PRIOR_6, u"5"), )
    group = StringField(max_length=128, default="None")
    name = StringField(max_length=128)
    type = StringField(max_length=20)
    timeout = IntField(default=200)
    status = IntField(default=STATUS_DEBUG, choices=STATUS_CHOICES)
    priority = IntField(default=PRIOR_6, choices=PRIOR_CHOICES)
    args = StringField(max_length=204800, null=True)
    info = StringField(max_length=1024)
    update_time = DateTimeField(default=datetime.datetime.now)
    add_time = DateTimeField(default=datetime.datetime.now)
    script = StringField(max_length=204800)
    models = StringField(max_length=10240)
    generator_interval = StringField(max_length=20)
    last_generator_time = DateTimeField()
    # downloader_interval = StringField(max_length=20)
    downloader_dispatch = IntField(default=60)
    # downloader_limit = IntField(default=3600)
    meta = {
        "db_alias": "oakling_project",
        "indexes": [
            "name"
        ]
    }
