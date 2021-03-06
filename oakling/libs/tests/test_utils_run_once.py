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
from collector.handler import CollectHandler
from collector.utils import OnceProcessor


# from django.test import TestCase

# Create your tests here.

class TestRunTaskDemo(unittest.TestCase):
    """
    Test Run Once Project Task Demo
    """
    def setUp(self):
        """
        Setup Initialization
        :return:
        """
        self.handler = CollectHandler()
        self.test_project_name = "test_run_once_demo_by_handler"
        self.test_project_name_by_utils = "test_run_once_demo_by_utils"
        self.test_invalid_path = "/tmp/unittest/test/nginx-test_run_once_demo_by_utils.log"
        self.test_valid_path = "/tmp/nginx-test_run_once_demo_by_utils.log"

    def tearDown(self):
        """
        Test completed
        """
        pass

    @unittest_log
    def test_run_once_demo_by_utils(self):
        """
        Test Run Once Demo By Utils
        :return:
        """
        # create project
        project_type = "Nginx"
        result = self.handler.create_project(self.test_project_name_by_utils, project_type)
        click.secho('%s \n' % result, fg='yellow', bg='black')

        once_processor = OnceProcessor()

        if os.path.exists(self.test_valid_path):
            os.remove(self.test_valid_path)

        config_args = {
            "num": 10,
            "output_path": self.test_valid_path
        }
        result = once_processor.run_processor(self.test_project_name_by_utils, **config_args)
        click.secho('Test valid Path: \n', fg='yellow', bg='black')
        click.secho('%s \n' % result, fg='yellow', bg='black')
        self.assertTrue(result["status"])

        with open(self.test_valid_path) as f:
            test_content = f.readline()
            self.assertTrue(isinstance(test_content, str))
            print "Read From Path:" + self.test_valid_path + "\n" + test_content

        config_args = {
            "num": 10,
            "output_path": self.test_invalid_path
        }
        result = once_processor.run_processor(self.test_project_name_by_utils, **config_args)
        click.secho('Test Invalid Path: \n', fg='yellow', bg='black')
        click.secho('%s \n' % result, fg='yellow', bg='black')
        self.assertFalse(result["status"])

        # drop project
        result = self.handler.drop_project(self.test_project_name_by_utils)
        click.secho('%s' % result, fg='yellow', bg='black')

    @unittest_log
    def test_run_once_demo_by_handler(self):
        """
        Test Run Once Demo By handler
        :return:
        """
        project_type = "Nginx"

        # Test project is not exist
        result = self.handler.run_once_processor(self.test_project_name)
        click.secho('%s \n' % result, fg='yellow', bg='black')
        self.assertTrue(result["status"])
        self.assertFalse(result["task"]["status"])

        # create project
        result = self.handler.create_project(self.test_project_name, project_type)
        click.secho('%s!' % result, fg='yellow', bg='black')

        # Test project is exist
        result = self.handler.run_once_processor(self.test_project_name)
        click.secho('%s \n' % result, fg='yellow', bg='black')
        self.assertTrue(result["status"])

        # drop project
        result = self.handler.drop_project(self.test_project_name)
        click.secho('%s' % result, fg='yellow', bg='black')



