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

class TestDemoSpider(unittest.TestCase):
    """
    Test Collector Utils DemoSpider Class
    """
    def setUp(self):
        """
        Setup Initialization
        :return:
        """
        self.demo = DemoSpider()

    def tearDown(self):
        """
        Test completed
        """
        pass

    @unittest_log
    def test_generator_nginx_log(self):
        """
        test generator nginx log
        :return:
        """
        nginx_log = self.demo.generator_nginx_log()

        click.secho('%s' % nginx_log, fg='yellow', bg='black')

        self.assertTrue(isinstance(nginx_log, str))

    @unittest_log
    def test_generator_nginx_log_by_num(self):
        """
        test generator nginx log by Number Parameter
        :return:
        """
        test_num = 10
        nginx_log = self.demo.generator_nginx_log_by_num(test_num)

        click.secho('%s' % nginx_log, fg='yellow', bg='black')

        self.assertTrue(isinstance(nginx_log, str))
        self.assertEqual(len(nginx_log.split("\n")), test_num)

    @unittest_log
    def test_save_to_file(self):
        """
        test save nginx log to file
        :return:
        """
        test_path = "/tmp/unittest_nginx_demo.log"
        if os.path.exists(test_path):
            os.remove(test_path)
        nginx_log = self.demo.generator_nginx_log_by_num(5)
        result = self.demo.save_to_file(nginx_log, test_path)

        self.assertTrue(result["status"])
        self.assertTrue(os.path.exists(test_path))

        with open(test_path) as f:
            test_content = f.readlines()
            lines = len(test_content)
            click.secho('%s' % test_content, fg='yellow', bg='black')

            self.assertTrue(isinstance(test_content, list))
            self.assertTrue(isinstance(test_content[0], str))
            self.assertEqual(lines, 5)

    @unittest_log
    def test_run_demo_spider(self):
        """
        Test run demo spider
        :return:
        """
        test_num = 1
        test_path = "/tmp/unittest_nginx_demo.log"

        if os.path.exists(test_path):
            os.remove(test_path)

        config_args = {
            "num": test_num,
            "output_path": test_path
        }
        result = self.demo.run(**config_args)
        click.secho('%s' % result, fg='yellow', bg='black')
        self.assertTrue(result["status"])


class TestDemoShell(unittest.TestCase):
    """
    Test Collector Utils DemoShell Class
    """
    def setUp(self):
        """
        Setup Initialization
        :return:
        """
        self.demo = DemoShell()

    def tearDown(self):
        """
        Test completed
        """
        pass

    @unittest_log
    def test_execute_shell_command(self):
        """
        test generator nginx log
        :return:
        """
        test_command = "ls -ll"
        result = self.demo.execute_shell(test_command)

        click.secho('%s' % result, fg='yellow', bg='black')
        self.assertTrue(result.get("status"))

    @unittest_log
    def test_run_demo_shell(self):
        """
        Test run demo shell
        :return:
        """
        test_command = "ls -ll"
        test_command = "echo 'Hello world'"

        config_args = {
            "command": test_command
        }
        result = self.demo.run(**config_args)

        click.secho('%s' % result, fg='yellow', bg='black')
        self.assertTrue(result["status"])

# Invalid Timeout Version
# 2017.6.7

# class TestUnitDebug(unittest.TestCase):
#     """
#     Test Collector Utils Processor Class
#     """
#     def setUp(self):
#         """
#         Setup Initialization
#         :return:
#         """
#         self.processor = Processor()
#
#     def tearDown(self):
#         """
#         Test completed
#         """
#         pass
#
#     @unittest_log
#     def test_run_processor(self):
#         """
#         Test run processor
#         :return:
#         """
#         test_num = 1
#         test_path = "/tmp/unittest_nginx.log"
#         if os.path.exists(test_path):
#             os.remove(test_path)
#
#         config_args = {
#             "num": test_num,
#             "output_path": test_path
#         }
#
#         result = self.processor.run_processor(**config_args)
#         self.assertTrue(result["status"])
#
#         with open(test_path) as f:
#             test_content = f.readline()
#             self.assertTrue(isinstance(test_content, str))
#             print "Read From Path:" + test_path + "\n" + test_content


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
        self.handler = CollectHandler()

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
        self.assertFalse(result["status"])

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



