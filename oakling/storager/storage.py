#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-03-2
# Project: Storager


import os
import arrow
from django.conf import settings


class Storage(object):
    """
    Storage data by type
    """

    def __init__(self, project_name):
        """
        Initialization
        """
        self.project_name = project_name.lower()

    def save_to_single_file(self, content, output_file, type="wb"):
        """
        Save content to single file
        :param content:
        :param type: "wb", "a"
        :param output_path:
        :return:
        """
        local_path = settings.LOCAL_DATAFILE_DIRS
        output_path = os.path.join(local_path, self.project_name, output_file)

        with open(output_path, type) as f:
            f.write(content)

        return {
            "status": True
        }

    def save_to_time_file(self, content, output_file, type="wb", formator='YYYY-MM-DD-HH'):
        """
        Save content to time formator file
        :param content: data
        :param type: "wb", "a"
        :param output_path: file_path
        :param formator: 'YYYY-MM-DD-HH-mm-ss',
                         'YYYY-MM-DD-HH-mm',
                         'YYYY-MM-DD-HH',
        :return:
        """
        local_path = settings.LOCAL_DATAFILE_DIRS

        # test.log ==> test{0}.log  ==> test-2017-7-7.log
        _output_file = output_file.split('.')
        if len(_output_file) >= 2:
            _output_file[-2] = _output_file[-2] + '-{0}'
            output_file = '.'.join(_output_file)
        else:
            output_file = output_file + '-{0}'

        output_path = os.path.join(local_path, self.project_name, output_file)

        with open(output_path.format(arrow.now().replace(hours=8).format(formator)), type) as f:
            f.write(content)

        return {
            "status": True
        }