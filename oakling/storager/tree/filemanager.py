#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.5.21
# Author: Oakling Group

"""
Oakling ./Tree/Content/File Manager

Reference: jupyter notebook filemanager

"""

import os
import stat
import errno
import _tz as tz
import logging
import mimetypes

import traceback
# from traitlets import (
#     Any,
#     Dict,
#     Instance,
#     List,
#     TraitError,
#     Type,
#     Unicode,
#     validate,
#     default,
# )

from fnmatch import fnmatch
from utils import is_hidden, is_file_hidden
from django.conf import settings
# from fileio import FileManagerMixin


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

from snakebite.client import Client

class FileContentsManager(object):
    """
    FileContent Manger
    """

    def __init__(self):

        self.log = logging

        self.root_dir = settings.LOCAL_DATAFILE_DIRS
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
            # self.root_dir = u'/tmp/data'

        self.hide_globs = [
            u'__pycache__', '*.pyc', '*.pyo',
            '.DS_Store', '*.so', '*.dylib', '*~',
        ]

    def should_list(self, name):
        """Should this file/directory name be displayed in a listing?"""
        return not any(fnmatch(name, glob) for glob in self.hide_globs)

    def _get_os_path(self, path):
        """Given an API path, return its file system path.

        Parameters
        ----------
        path : string
            The relative API path to the named file.

        Returns
        -------
        path : string
            Native, absolute OS path to for a file.

        Raises
        ------
        404: if path is outside root
        """
        root = os.path.abspath(self.root_dir)
        os_path = to_os_path(path, root)
        if not (os.path.abspath(os_path) + os.path.sep).startswith(root):
            raise ValueError(4040, "%s is outside root contents directory" % path)
        return os_path

    def is_hidden(self, path):
        """Does the API style path correspond to a hidden directory or file?

        Parameters
        ----------
        path : string
            The path to check. This is an API path (`/` separated,
            relative to root_dir).

        Returns
        -------
        hidden : bool
            Whether the path exists and is hidden.
        """
        path = path.strip('/')
        os_path = self._get_os_path(path=path)
        return is_hidden(os_path, self.root_dir)

    def exists(self, path):
        """Returns True if the path exists, else returns False.

        API-style wrapper for os.path.exists

        Parameters
        ----------
        path : string
            The API path to the file (with '/' as separator)

        Returns
        -------
        exists : bool
            Whether the target exists.
        """
        path = path.strip('/')
        os_path = self._get_os_path(path=path)
        return os.path.exists(os_path)

    def _base_model(self, path):
        """Build the common base of a contents model"""
        os_path = self._get_os_path(path)
        info = os.stat(os_path)
        last_modified = tz.localfromtimestamp(info.st_mtime)
        created = tz.localfromtimestamp(info.st_ctime)
        # Create the base model.
        model = {}
        model['name'] = path.rsplit('/', 1)[-1]
        model['path'] = path
        model['last_modified'] = last_modified
        model['created'] = created
        model['content'] = None
        model['format'] = None
        model['mimetype'] = None
        try:
            model['writable'] = os.access(os_path, os.W_OK)
        except OSError:
            self.log.error("Failed to check write permissions on %s", os_path)
            model['writable'] = False
        return model

    def _dir_model(self, path, content=True):
        """Build a model for a directory

        if content is requested, will include a listing of the directory
        """
        os_path = self._get_os_path(path)

        four_o_four = u'directory does not exist: %r' % path

        if not os.path.isdir(os_path):
            return {
                "status": False,
                "msg": (4040, four_o_four)
            }
        elif is_hidden(os_path, self.root_dir):
            # self.log.info("Refusing to serve hidden directory %r, via 404 Error",
            #               os_path
            #               )
            return {
                "status": False,
                "msg": (4040, u'"Refusing to serve hidden directory %s' % (path))
            }

        model = self._base_model(path)
        model['type'] = 'directory'
        if content:
            model['content'] = contents = []
            os_dir = self._get_os_path(path)
            for name in os.listdir(os_dir):
                try:
                    os_path = os.path.join(os_dir, name)
                except UnicodeDecodeError as e:
                    self.log.warning(
                        "failed to decode filename '%s': %s", name, e)
                    continue

                try:
                    st = os.stat(os_path)
                except OSError as e:
                    # skip over broken symlinks in listing
                    if e.errno == errno.ENOENT:
                        self.log.warning("%s doesn't exist", os_path)
                    else:
                        self.log.warning("Error stat-ing %s: %s", (os_path, e))
                    continue

                if not stat.S_ISREG(st.st_mode) and not stat.S_ISDIR(st.st_mode):
                    self.log.debug("%s not a regular file", os_path)
                    continue

                if self.should_list(name) and not is_file_hidden(os_path, stat_res=st):
                    contents.append(self.get(
                        path='%s/%s' % (path, name),
                        content=False)
                    )

            model['format'] = 'json'

        return model

    def _file_model(self, path, content=True, format=None):
        """Build a model for a file

        if content is requested, include the file contents.

        format:
          If 'text', the contents will be decoded as UTF-8.
          If 'base64', the raw bytes contents will be encoded as base64.
          If not specified, try to decode as UTF-8, and fall back to base64
        """
        model = self._base_model(path)
        model['type'] = 'file'

        os_path = self._get_os_path(path)
        model['mimetype'] = mimetypes.guess_type(os_path)[0]

        if content:
            content, format = self._read_file(os_path, format)
            if model['mimetype'] is None:
                default_mime = {
                    'text': 'text/plain',
                    'base64': 'application/octet-stream'
                }[format]
                model['mimetype'] = default_mime

            model.update(
                content=content,
                format=format,
            )

        return model

    def _notebook_model(self, path, content=True):
        """Build a notebook model

        if content is requested, the notebook content will be populated
        as a JSON structure (not double-serialized)
        """
        model = self._base_model(path)
        model['type'] = 'notebook'
        if content:
            os_path = self._get_os_path(path)
            nb = self._read_notebook(os_path, as_version=4)
            # self.mark_trusted_cells(nb, path)
            model['content'] = nb
            model['format'] = 'json'
            # self.validate_notebook_model(model)
        return model

    def get(self, path, content=True, type=None, format=None):
        """ Takes a path for an entity and returns its model

        Parameters
        ----------
        path : str
            the API path that describes the relative path for the target
        content : bool
            Whether to include the contents in the reply
        type : str, optional
            The requested type - 'file', 'notebook', or 'directory'.
            Will raise HTTPError 400 if the content doesn't match.
        format : str, optional
            The requested format for file contents. 'text' or 'base64'.
            Ignored if this returns a notebook or directory model.

        Returns
        -------
        model : dict
            the contents model. If content=True, returns the contents
            of the file or directory as well.
        """
        path = path.strip('/')

        if not self.exists(path):
            return {
                "status": False,
                "msg": (4040, u'No such file or directory: %s' % path)
            }

        os_path = self._get_os_path(path)
        if os.path.isdir(os_path):
            if type not in (None, 'directory'):
                return {
                    "status": False,
                    "msg": (4000, u'%s is not a directory, not a %s' % (path, type))
                }

                # raise web.HTTPError(400,
                #                     u'%s is a directory, not a %s' % (path, type), reason='bad type')

            model = self._dir_model(path, content=content)

        # elif type == 'notebook' or (type is None and path.endswith('.ipynb')):
        #     model = self._notebook_model(path, content=content)

        else:
            if type == 'directory':
                return {
                    "status": False,
                    "msg": (4000, u'%s is a directory' % (path))
                }

                # raise web.HTTPError(400,
                #                     u'%s is not a directory' % path, reason='bad type')

            model = self._file_model(path, content=content, format=format)

        # return model
        return {
            "status": True,
            "msg": "Query path: %s succeed." %(path),
            "data": model
        }


class HdfsFileContentsManager(object):
    """
    FileContent Manger
    """

    def __init__(self):
        """
        Initialization
        """
        self.log = logging
        self.root_dir = settings.HDFS_DATAFILE_DIRS

        hdfs_namenode_host = settings.HDFS_NAMENODE_HOST
        hdfs_namenode_port = settings.HDFS_NAMENODE_PORT

        self.client = Client(hdfs_namenode_host, hdfs_namenode_port, use_trash=False)

        for i in self.client.ls([self.root_dir]):
            print i

        try:
            self.client.stat([self.root_dir])
        except FileNotFoundException:
            result = self.client.mkdir([self.root_dir]).next()
            if result['result'] is True:
                self.log.info("Sucessfully create HDFS root data path %s " %(self.root_dir))
        # except Exception:
        #     print traceback.format_exc()

        self.hide_globs = [
            u'__pycache__', '*.pyc', '*.pyo',
            '.DS_Store', '*.so', '*.dylib', '*~',
        ]

    def should_list(self, name):
        """Should this file/directory name be displayed in a listing?"""
        return not any(fnmatch(name, glob) for glob in self.hide_globs)

    def _get_os_path(self, path):
        """Given an API path, return its file system path.

        Parameters
        ----------
        path : string
            The relative API path to the named file.

        Returns
        -------
        path : string
            Native, absolute OS path to for a file.

        Raises
        ------
        404: if path is outside root
        """
        # root = os.path.abspath(self.root_dir)
        # os_path = to_os_path(path, root)
        # if not (os.path.abspath(os_path) + os.path.sep).startswith(root):
        #     raise ValueError(4040, "%s is outside root contents directory" % path)
        # return os_path

        root = self.root_dir
        os_path = to_os_path(path, root)
        if not (os_path + os.path.sep).startswith(root):
            raise ValueError(4040, "%s is outside root contents directory" % path)
        return os_path

    def is_hidden(self, path):
        """Does the API style path correspond to a hidden directory or file?

        Parameters
        ----------
        path : string
            The path to check. This is an API path (`/` separated,
            relative to root_dir).

        Returns
        -------
        hidden : bool
            Whether the path exists and is hidden.
        """
        path = path.strip('/')
        os_path = self._get_os_path(path=path)
        return is_hidden(os_path, self.root_dir)

    def exists(self, path):
        """Returns True if the path exists, else returns False.

        API-style wrapper for os.path.exists

        Parameters
        ----------
        path : string
            The API path to the file (with '/' as separator)

        Returns
        -------
        exists : bool
            Whether the target exists.
        """
        path = path.strip('/')
        os_path = self._get_os_path(path=path)

        print "439: os_path", os_path

        try:
            self.client.stat([os_path])
            return True
        except FileNotFoundException:
            return False
        # except Exception:
        #     return False

    def _base_model(self, path):
        """Build the common base of a contents model"""
        os_path = self._get_os_path(path)
        # info = os.stat(os_path)
        info = self.client.stat([os_path])

        print "452, info:", info

        last_modified = tz.localfromtimestamp(float(info["modification_time"])/1000)
        created = tz.localfromtimestamp(float(info["modification_time"])/1000)
        # Create the base model.
        model = {}
        model['name'] = path.rsplit('/', 1)[-1]
        model['path'] = path
        model['last_modified'] = last_modified
        model['created'] = created
        model['content'] = None
        model['format'] = None
        model['mimetype'] = None
        try:
            # model['writable'] = os.access(os_path, os.W_OK)
            model['writable'] = True
        except OSError:
            self.log.error("Failed to check write permissions on %s", os_path)
            model['writable'] = False
        return model

    def _dir_model(self, path, content=True):
        """Build a model for a directory

        if content is requested, will include a listing of the directory
        """
        os_path = self._get_os_path(path)

        four_o_four = u'directory does not exist: %r' % path

        # if not os.path.isdir(os_path):
        #     return {
        #         "status": False,
        #         "msg": four_o_four,
        #         "code": 4040
        #     }
        # elif is_hidden(os_path, self.root_dir):
        #     # self.log.info("Refusing to serve hidden directory %r, via 404 Error",
        #     #               os_path
        #     #               )
        #     return {
        #         "status": False,
        #         "msg":  u'"Refusing to serve hidden directory %s' % (path),
        #         "code": 4040
        #     }

        print "495:path", path

        model = self._base_model(path)
        model['type'] = 'directory'
        if content:
            model['content'] = contents = []
            os_dir = self._get_os_path(path)
            os_listdir = [i for i in self.client.ls([os_dir])]

            # for name in os.listdir(os_dir):
            for index, name in enumerate(os_listdir):
                # index += 1
                # if index >= 20:
                #     break
                os_path = name['path']
                _name = name["path"].split("/")[-1]

                # try:
                #     st = os.stat(os_path)
                # except OSError as e:
                #     # skip over broken symlinks in listing
                #     if e.errno == errno.ENOENT:
                #         self.log.warning("%s doesn't exist", os_path)
                #     else:
                #         self.log.warning("Error stat-ing %s: %s", (os_path, e))
                #     continue

                # if not stat.S_ISREG(st.st_mode) and not stat.S_ISDIR(st.st_mode):
                #     self.log.debug("%s not a regular file", os_path)
                #     continue

                # if self.should_list(name) and not is_file_hidden(os_path, stat_res=st):

                # print "531,name",  name["path"].split("/")[-1]

                if self.should_list(_name):
                    contents.append(self.get(
                        path='%s/%s' % (path, _name),
                        content=False)
                    )

            model['format'] = 'json'

        return model

    def _file_model(self, path, content=True, format=None):
        """Build a model for a file

        if content is requested, include the file contents.

        format:
          If 'text', the contents will be decoded as UTF-8.
          If 'base64', the raw bytes contents will be encoded as base64.
          If not specified, try to decode as UTF-8, and fall back to base64
        """
        model = self._base_model(path)
        model['type'] = 'file'

        os_path = self._get_os_path(path)
        model['mimetype'] = mimetypes.guess_type(os_path)[0]

        # if content:
        #     content, format = self._read_file(os_path, format)
        #     if model['mimetype'] is None:
        #         default_mime = {
        #             'text': 'text/plain',
        #             'base64': 'application/octet-stream'
        #         }[format]
        #         model['mimetype'] = default_mime
        #
        #     model.update(
        #         content=content,
        #         format=format,
        #     )

        return model

    def _notebook_model(self, path, content=True):
        """Build a notebook model

        if content is requested, the notebook content will be populated
        as a JSON structure (not double-serialized)
        """
        model = self._base_model(path)
        model['type'] = 'notebook'
        if content:
            os_path = self._get_os_path(path)
            nb = self._read_notebook(os_path, as_version=4)
            # self.mark_trusted_cells(nb, path)
            model['content'] = nb
            model['format'] = 'json'
            # self.validate_notebook_model(model)
        return model

    def get(self, path, content=True, type=None, format=None):
        """ Takes a path for an entity and returns its model

        Parameters
        ----------
        path : str
            the API path that describes the relative path for the target
        content : bool
            Whether to include the contents in the reply
        type : str, optional
            The requested type - 'file', 'notebook', or 'directory'.
            Will raise HTTPError 400 if the content doesn't match.
        format : str, optional
            The requested format for file contents. 'text' or 'base64'.
            Ignored if this returns a notebook or directory model.

        Returns
        -------
        model : dict
            the contents model. If content=True, returns the contents
            of the file or directory as well.
        """
        path = path.strip('/')

        # print "615: path", path

        if not self.exists(path):
            return {
                "status": False,
                "msg": (4040, u'No such file or directory: %s' % path)
            }

        os_path = self._get_os_path(path)
        path_stat = self.client.stat([os_path])

        # if os.path.isdir(os_path):
        if path_stat["file_type"] == 'd':
            if type not in (None, 'directory'):
                return {
                    "status": False,
                    "msg": (4000, u'%s is not a directory, not a %s' % (path, type))
                }

                # raise web.HTTPError(400,
                #                     u'%s is a directory, not a %s' % (path, type), reason='bad type')

            model = self._dir_model(path, content=content)

        # elif type == 'notebook' or (type is None and path.endswith('.ipynb')):
        #     model = self._notebook_model(path, content=content)

        else:
            if type == 'directory':
                return {
                    "status": False,
                    "msg": (4000, u'%s is a directory' % (path))
                }

                # raise web.HTTPError(400,
                #                     u'%s is not a directory' % path, reason='bad type')

            model = self._file_model(path, content=content, format=format)

        # return model
        return {
            "status": True,
            "msg": "Query path: %s succeed." %(path),
            "data": model
        }


def to_os_path(path, root=''):
    """Convert an API path to a filesystem path

    If given, root will be prepended to the path.
    root must be a filesystem path already.
    """
    parts = path.strip('/').split('/')
    parts = [p for p in parts if p != '']  # remove duplicate splits
    path = os.path.join(root, *parts)
    return path