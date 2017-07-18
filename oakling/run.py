#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.5.21
# Author: Oakling Group

"""
Oakling Run Management

"""

import os
import click
import string
import datetime
import traceback

from libs import pprint
from collector.handler import CollectHandler
from scheduler.scheduler import Scheduler
from libs.signal.signal import *

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oakling.settings")

# try:
#     from django.core.management import execute_from_command_line
# except ImportError:
#     # The above import may fail for some other reason. Ensure that the
#     # issue is really that Django is missing to avoid masking other
#     # exceptions on Python 2.
#     try:
#         import django
#     except ImportError:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         )

from django.conf import settings

# Basic Info

def print_version(ctx, param, value):
    """
    Print Oakling Version
    :param ctx:
    :param param:
    :param value:
    :return:
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo(settings.VERSION)
    ctx.exit()


# Command Management

@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Oakling Version')
def cli():
    """
    start program
    """


@cli.command()
@click.option('--name', prompt='Your Project Name', help='Project Name.')
@click.option('--project_type', prompt='Your Project Type', help='Project Type.')
def start_project(name, project_type):
    """
    Start new project
    :param name: project name
    :return: status
    """
    # click.echo('Hello %s!' % name)
    # click.secho('Hello %s!' % name, fg='red', underline=False)
    # click.secho('Hello %s!' % name, fg='yellow', bg='black')

    handler = CollectHandler()
    result = handler.create_project(name, project_type)
    click.secho('%s!' % result, fg='yellow', bg='black')


@cli.command()
@click.option('--name', prompt='Your Project Name', help='Project Name.')
@click.confirmation_option(prompt='Are you sure you want to drop the project?')
def drop_project(name):
    """
    Drop project by project name
    :param name: project name
    :return: status
    """
    handler = CollectHandler()
    result = handler.drop_project(name)
    click.secho('%s' % result, fg='yellow', bg='black')


@cli.command()
@click.option('--name', prompt='Your Project Name', help='Project Name.')
def run_once(name):
    """
    Run once project processor
    :param name: project name
    :return: status
    """
    handler = CollectHandler()
    result = handler.run_once_processor(name)
    click.secho('%s' % result, fg='yellow', bg='black')


@cli.command()
def run_scheduler():
    """
    Run scheduler
    """
    scheduler = Scheduler()
    scheduler.run()


@cli.command()
def run_signal():
    """
    Run signal websocket server
    """
    click.secho('Start signal websocket server, Port::8080', fg='yellow', bg='black')
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()


# Unittest Module

@cli.command()
def run_test():
    """
    Run oakling unittest
    :return:
    """
    import subprocess
    runner = subprocess.Popen('python manage.py test', shell=True)
    runner.wait()
    click.secho('Run Unittest Finished!', fg='yellow', underline=False)


def main():
    cli()

if __name__ == '__main__':
    main()


