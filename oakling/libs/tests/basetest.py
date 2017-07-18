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

from collector.utils import DemoSpider
from collector.utils import DemoShell
from collector.utils import Processor
from collector.handler import Handler
from collector.utils import OnceProcessor


# from django.test import TestCase

# Create your tests here.

def unittest_log(func):
    """
    Unittest Log
    :param func:
    :return:
    """
    def wrapper(*args, **kw):
        """
        Function Warpper
        :param args:
        :param kw:
        :return:
        """
        start_time=time.time()
        _time = arrow.now()

        click.secho("  \n \n")
        click.secho("[ INFO ] {0}{1}".format("="*60, "="*60), fg='green', underline=False)
        click.secho("[ INFO ] Start Unittest Case", fg='green', underline=False)
        click.secho("[ INFO ] Case Name: {0}".format(func.__name__), fg='green', underline=False)
        click.secho("[ INFO ] Start Time: {0} \n".format(_time), fg='green', underline=False)

        data = func(*args, **kw)
        end_time = time.time()

        click.secho(" ")
        click.secho("[ INFO ] Spend Time: {0} s".format(end_time-start_time), fg='green', underline=False)
        click.secho("[ INFO ] Finished Unittest Case", fg='green', underline=False)
        click.secho("[ INFO ] {0}{1} \n \n".format("="*60, "="*60))

        return data

    return wrapper


