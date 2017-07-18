#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author:  Oakling Group
# Created on 2017.6.1
# Usage: Python manage.py test

from __future__ import unicode_literals

import os
import time
import arrow
import click
import unittest2 as unittest

from libs.tests.basetest import unittest_log
from collector.utils import DemoSpider
from collector.utils import DemoShell
from collector.utils import Processor
from collector.handler import Handler
from collector.utils import OnceProcessor


# from django.test import TestCase

# Create your tests here.


class TestCreateMongodbModels(unittest.TestCase):
    """
    Test Create Project Mongodb Models
    """
    def setUp(self):
        """
        Setup Initialization
        :return:
        """
        self.test_project_name = "unittest_project"
        self.handler = Handler()

    @unittest_log
    def test_create_project(self):
        """
        Test Create Project
        :return:
        """
        project_type = "nginx"
        result = self.handler.create_project(self.test_project_name, project_type)
        click.secho('%s' % result, fg='yellow', bg='black')
        self.assertTrue(result["status"])

    @unittest_log
    def test_create_invalid_project(self):
        """
        Test Create Project
        :return:
        """
        project_type = "xxxxxxxxxxxxxxx"
        result = self.handler.create_project(self.test_project_name, project_type)
        click.secho('%s' % result, fg='yellow', bg='black')
        self.assertFalse(result["status"])

    @unittest_log
    def test_drop_project(self):
        """
        Test Drop Project
        :return:
        """
        result = self.handler.drop_project(self.test_project_name)
        click.secho('%s' % result, fg='yellow', bg='black')
        self.assertTrue(result["status"])

    @unittest_log
    def test_query_project(self):
        """
        Test Create Project
        :return:
        """
        project_type = "nginx"
        project_check_name = None
        test_project_query_name = "unittest_project_query"

        result = self.handler.create_project(test_project_query_name, project_type)
        click.secho('%s!' % result, fg='yellow', bg='black')

        result = self.handler.query_project(test_project_query_name)

        for _project in result:
            click.secho('project name: %s' % _project.name, fg='yellow', bg='black')
            click.secho('project status: %s' % _project.status, fg='yellow', bg='black')
            click.secho('project add_time: %s' % _project.add_time, fg='yellow', bg='black')
            click.secho('project script length: %s' % len(_project.script), fg='yellow', bg='black')
            project_check_name = _project.name

        self.assertEqual(test_project_query_name, project_check_name)

        result = self.handler.drop_project(test_project_query_name)
        click.secho('%s' % result, fg='yellow', bg='black')