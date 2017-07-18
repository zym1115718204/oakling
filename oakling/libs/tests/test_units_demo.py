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
        self.assertEqual(len(nginx_log.strip().split("\n")), test_num)

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