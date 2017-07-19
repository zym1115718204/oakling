#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-03-2
# Project:  Storager Handler

import os
import time
import json
import redis
import string
import codecs
import arrow
import psutil
import datetime
import traceback
import logging

from storager.tree import _tz as tz
from django.conf import settings
from django.utils.encoding import smart_unicode

from libs.database.mongodb.projectdb import Project


class StorageHandler(object):
    """
    Oakling Storage Handler Route Module
    """
    def __init__(self):
        """
        Parameters Initialization
        """
        activate = settings.BASE_DIR
        self._query = Query()
        # self._command = Command()

    def query_data_systems_status(self):
        """
        Query DataSystems Status Route
        :return:
        """
        result = self._query.query_data_systems_status()
        return result

    def query_data_systems_status_by_project(self, name, type):
        """
        Query DataSystems Status By project Route
        :return:
        """
        result = self._query.query_data_systems_status_by_project(name, type)
        return result


class Query(object):
    """
    Query Handler
    """

    def __init__(self):
        """
        Initialization
        """
        pass

    def query_data_systems_status(self):
        """
        Get Datasystem
        ["LOCALFILE", "HDFS"]
        :return:
        """
        data_systems_status = {}
        data_systems_config = settings.REGISTER_DATASYSTEMS

        if data_systems_config is None or (not isinstance(data_systems_config, list)):
            return {
                "status": False,
                "msg": "Settings.py Error, REGISTER_DATASYSTEMS is not found!"
            }
        else:
            if "LOCAL" in data_systems_config:
                local_status = self.query_local_system_status()
                data_systems_status["LOCAL"] = local_status

            if "HDFS" in data_systems_config:
                hdfs_status = self.query_hdfs_system_status()
                data_systems_status["HDFS"] = hdfs_status

            if data_systems_status:
                return {
                    "status": True,
                    "datasystems": data_systems_status,
                    "msg": "Successfully to query data system status."
                }

    def query_data_systems_status_by_project(self, name, type):
        """
        Get Datasystem
        ["LOCALFILE", "HDFS"]
        :return:
        """
        project_status = {}
        data_systems_config = settings.REGISTER_DATASYSTEMS

        if data_systems_config is None or (not isinstance(data_systems_config, list)):
            return {
                "status": False,
                "msg": "Settings.py Error, REGISTER_DATASYSTEMS is not found!"
            }
        else:
            if "LOCAL" in data_systems_config and type == "LOCAL":
                root_dir = settings.LOCAL_DATAFILE_DIRS
                project_status = self.query_local_system_status_by_project(name, root_dir)

            elif "HDFS" in data_systems_config and type == "HDFS":

                from snakebite.client import Client

                if settings.HDFS_NAMENODE_HOST and settings.HDFS_NAMENODE_PORT and settings.HDFS_DATAFILE_DIRS:
                    hdfs_namenode_host = settings.HDFS_NAMENODE_HOST
                    hdfs_namenode_port = settings.HDFS_NAMENODE_PORT
                    root_dir = settings.HDFS_DATAFILE_DIRS
                    client = Client(hdfs_namenode_host, hdfs_namenode_port, use_trash=False)

                    for i, path in enumerate(client.du([root_dir])):
                        if path["path"] == os.path.join(root_dir, name):
                            _path = path
                            project_status = self.query_hdfs_system_status_by_project(client, _path)

                else:
                    return{
                        "status": False,
                        "project": project_status,
                        "msg": "Failed to query project %s data status.reason: No HDFS_NAMENODET" % (name,)
                }

            if project_status:
                return {
                    "status": True,
                    "project": project_status,
                    "msg": "Successfully to query project %s data system status." % (name,)
                }


    def query_local_system_status(self):
        """
        Get local filesystem status
        :return:
        """
        _local_config = {
            "type": "local",
            "config": None,
            "path": "",
            "projects": [],
            "connected": False,
            "spaceConsumed": 0,
            "length": 0,
            "modification_time": "",

            # Disk Info
            "capacity": 0,
            "used": 0,
            "remaining": 0,
            "used_percent": 0
        }
        if settings.LOCAL_DATAFILE_DIRS:
            root_dir = settings.LOCAL_DATAFILE_DIRS
            _local_config["config"] = root_dir
            _local_config["path"] = root_dir

            if os.path.exists(root_dir):
                _local_config["connected"] = True
            else:
                try:
                    os.makedirs(root_dir)
                except Exception:
                    logging.error("Make localFile data path failed. Reason: %s" %(traceback.format_exc()))
                    return _local_config
                _local_config["connected"] = True

            _local_config["fileCount"] = sum([len(x) for _, _, x in os.walk(os.path.dirname(root_dir))])

            # os status
            from storager.tree import _tz as tz

            info = os.stat(root_dir)
            last_modified = tz.localfromtimestamp(float(info.st_mtime))
            created = tz.localfromtimestamp(float(info.st_ctime))

            _local_config["modification_time"] = last_modified
            _local_config["created"] = created

            # disk info
            sdiskusage = psutil.disk_usage(root_dir)

            _local_config["length"] = float(self.FileSize(root_dir)) / 1024 / 1024 / 1024   # Byte =》GB
            _local_config["capacity"] = float(sdiskusage.total)/1024/1024/1024   # Byte =》GB
            _local_config["used"] = float(sdiskusage.used)/1024/1024/1024   # Byte =》GB
            _local_config["remaining"] = float(sdiskusage.free)/1024/1024/1024   # Byte =》GB
            _local_config["used_percent"] = sdiskusage.percent

            try:
                for i, name in enumerate(os.listdir(root_dir)):
                    project = self.query_local_system_status_by_project(name, root_dir, index=i)
                    _local_config["projects"].append(project)

            except Exception:
                logging.error(traceback.format_exc())
                _local_config["connected"] = False
                return _local_config

        return _local_config

    def query_local_system_status_by_project(self, name, root_dir, index=0):
        """
        Query data systems status by project
        :param name:
        :param root_dir: LocalFile root_dir
        :param index:
        :return:
        """
        project = {}
        project["project"] = name
        project["name"] = name

        project["index"] = index % 8
        project["path"] = os.path.join(root_dir, name)
        project["length"] = float(self.FileSize(project["path"])) / 1024 / 1024 / 1024  # Byte =》GB
        project["fileCount"] = sum([len(x) for _, _, x in os.walk(project["path"])])

        info = os.stat(os.path.join(root_dir, name))

        last_modified = tz.localfromtimestamp(info.st_mtime)
        created = tz.localfromtimestamp(info.st_ctime)

        project["modification_time"] = last_modified
        project["created"] = created

        return project

    def query_hdfs_system_status(self):
        """
        Get HDFS filesystem status
        """
        _hdfs_config = {
            "type": "hdfs",

            # DataFile
            "config": None,
            "path": None,
            "owner": None,
            "permission": None,
            "projects": [],
            "connected": False,
            "spaceConsumed": 0,
            "length": 0,
            "modification_time": "",

            # Total HDFS
            "capacity": 0,
            "filesystem": None,
            "corrupt_blocks": 0,
            "missing_blocks": 0,
            "remaining": 0,
            "under_replicated": 0,
            "used": 0,
            "used_percent": 0

            # permission
        }

        from snakebite.errors import (
            ConnectionFailureException,
            DirectoryException,
            FileAlreadyExistsException,
            FileException,
            FileNotFoundException,
            InvalidInputException,
            OutOfNNException,
            RequestError,
            FatalException, TransientException)

        from socket import gaierror
        from snakebite.client import Client

        if settings.HDFS_NAMENODE_HOST and settings.HDFS_NAMENODE_PORT and settings.HDFS_DATAFILE_DIRS:

            hdfs_namenode_host = settings.HDFS_NAMENODE_HOST
            hdfs_namenode_port = settings.HDFS_NAMENODE_PORT
            root_dir = settings.HDFS_DATAFILE_DIRS

            _hdfs_config["config"] = "{0}:{1}".format(hdfs_namenode_host, hdfs_namenode_port)
            _hdfs_config["path"] = root_dir

            client = Client(hdfs_namenode_host, hdfs_namenode_port, use_trash=False)

            # Check HDFS connection
            """
            Client df:
                {'capacity': 545188233216L,
                 'corrupt_blocks': 0L,
                 'filesystem': 'hdfs://namenode:8020',
                 'missing_blocks': 0L,
                 'remaining': 421691441152L,
                 'under_replicated': 0L,
                 'used': 120569511936L}
            """
            try:
                result = client.df()
                _hdfs_config["connected"] = True
                _hdfs_config["capacity"] = float(result.get("capacity", 0))/1000/1024/1024  # Byte => GB
                _hdfs_config["corrupt_blocks"] = result.get("corrupt_blocks", 0)
                _hdfs_config["filesystem"] = result.get("filesystem", "")
                _hdfs_config["remaining"] = float(result.get("remaining", 0))/1000/1024/1024  # yte => GB
                _hdfs_config["under_replicated"] = result.get("under_replicated", 0)
                _hdfs_config["used"] = float(result.get("used", 0))/1000/1024/1024  # Byte => GB
                _hdfs_config["used_percent"] =  _hdfs_config["used"] * 100/_hdfs_config["capacity"]  # %

            except gaierror:
                # print traceback.format_exc()
                return _hdfs_config

            # Check Data directorys status
            """
             Client.stat demo:
                {'access_time': 0L,
                 'block_replication': 0,
                 'blocksize': 0L,
                 'file_type': 'd',
                 'group': u'hdfs',
                 'length': 0L,
                 'modification_time': 1499320215393L,
                 'owner': u'princetechs',
                 'path': '/tmp/data',
                 'permission': 493}
            """
            try:
                status = client.stat([root_dir])

            except gaierror:
                # print traceback.format_exc()

                _hdfs_config["connected"] = False
                return _hdfs_config

            except FileNotFoundException:
                # print traceback.format_exc()

                result = client.mkdir([root_dir]).next()
                if result['result'] is True:
                    print "Sucessfully create HDFS root data path %s " % (root_dir)

            status = client.stat([root_dir])

            _modification_time = status.get("modification_time", "")
            if _modification_time:
                _modification_time = tz.utcfromtimestamp(float(_modification_time)/1000)

            _hdfs_config["owner"] = status.get("owner", None)
            _hdfs_config["permission"] = status.get("permission", None)
            _hdfs_config["modification_time"] = _modification_time
            _hdfs_config["group"] = status.get("group", None)

            # Checkout Data directorys counts
            """
            Demo:
                {'spaceConsumed': 34669594392L, 'quota': 18446744073709551615L,
                'spaceQuota': 18446744073709551615L, 'length': 11556531464L,
                'directoryCount': 4L, 'path': '/tmp/data', 'fileCount': 674L}
            """
            try:
                count = client.count([root_dir]).next()
            except gaierror:
                _hdfs_config["connected"] = False
                return _hdfs_config

            _hdfs_config["length"] = float(count.get("length", 0))/1000/1024/1024  # Byte =》GB
            _hdfs_config["spaceConsumed"] = float(count.get("spaceConsumed", 0))/1000/1024/1024  # Byte =》GB
            _hdfs_config["directoryCount"] = float(count.get("directoryCount", 0))
            _hdfs_config["fileCount"] = float(count.get("fileCount", 0))

            # Checkout Projects path
            """
            {'path': '/tmp/data/demo', 'length': 11556531464L}
            {'path': '/tmp/data/demo2', 'length': 0L}

            """
            try:
                for i, path in enumerate(client.du([root_dir])):
                    try:
                        project = self.query_hdfs_system_status_by_project(client, path, index=i)
                        _hdfs_config["projects"].append(project)

                    except gaierror:
                        # print traceback.format_exc()
                        _hdfs_config["connected"] = False
                        return _hdfs_config

                return _hdfs_config

            except gaierror:
                print traceback.format_exc()
                return _hdfs_config

    def query_hdfs_system_status_by_project(self, client, path, index=0):
        """
        Query Hdfs systems status by project
        :param path:
        :param index:
        :return:
        """
        project = {}
        project["project"] = path['path'].split('/')[-1]
        project["name"] = project["project"]
        project["index"] = index % 8
        project["path"] = path['path']
        project["length"] = float(path['length']) / 1000 / 1024 / 1024

        count = client.count([path['path']]).next()
        project["length"] = float(count.get("length", 0)) / 1000 / 1024 / 1024  # Byte =》GB
        project["spaceConsumed"] = float(
            count.get("spaceConsumed", 0)) / 1000 / 1024 / 1024  # Byte =》GB
        project["directoryCount"] = int(count.get("directoryCount", 0))
        project["fileCount"] = int(count.get("fileCount", 0))

        status = client.stat([path['path']])
        _modification_time = status.get("modification_time", "")
        if _modification_time:
            _modification_time = tz.utcfromtimestamp(float(_modification_time)/1000)
        project["owner"] = status.get("owner", None)
        project["permission"] = status.get("permission", None)
        project["modification_time"] = _modification_time
        project["group"] = status.get("group", None)

        return project

    @staticmethod
    def FileSize(path):
        size = 0
        for root, dirs, files in os.walk(path, True):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size

