#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.5.21
# Author: Oakling Group

"""
Oakling Tree Handler
"""

from django.conf import settings

from filemanager import FileContentsManager, HdfsFileContentsManager
from utils import url_path_join, url_escape

try:
    from urllib.parse import quote, unquote, urlparse
except ImportError:
    from urllib import quote, unquote
    from urlparse import urlparse


#-----------------------------------------------------------------------------
# URL pattern fragments for re-use
#-----------------------------------------------------------------------------

# path matches any number of `/foo[/bar...]` or just `/` or ''
path_regex = r"(?P<path>(?:(?:/[^/]+)+|/?))"

#-----------------------------------------------------------------------------
# URL to handler mappings
#-----------------------------------------------------------------------------


class ContentsManager():
    """
    Tree Content Manager
    """

    def dir_exists(self, path):
        return True

    def file_exists(self, path):
        return True

    def is_hidden(self, path):
        return False


def sort_key(model):
    """key function for case-insensitive sort by name and type"""
    iname = model['data']['name'].lower()
    type_key = {
        'directory' : '0',
        'notebook'  : '1',
        'file'      : '2',
    }.get(model['data']['type'], '9')
    return u'%s%s' % (type_key, iname)


def validate_model(model, expect_content):
    """
    Validate a model returned by a ContentsManager method.

    If expect_content is True, then we expect non-null entries for 'content'
    and 'format'.
    """
    required_keys = {
        "name",
        "path",
        "type",
        "writable",
        "created",
        "last_modified",
        "mimetype",
        "content",
        "format",
    }
    missing = required_keys - set(model.keys())
    if missing:
        return {
            "status": False,
            "msg": u"Missing Model Keys: {missing}".format(missing=missing),
            "code": 5000
        }

    maybe_none_keys = ['content', 'format']
    if expect_content:
        errors = [key for key in maybe_none_keys if model[key] is None]
        if errors:
            return {
                "status": False,
                "msg": u"Keys unexpectedly None: {keys}".format(keys=errors),
                "code": 5000
            }

    else:
        errors = {
            key: model[key]
            for key in maybe_none_keys
            if model[key] is not None
        }
        if errors:
            return {
                "status": False,
                "msg": u"Keys unexpectedly not None: {keys}".format(keys=errors),
                "code": 5000
            }


class TreeHandler(object):
    """Render the tree view, listing notebooks, etc."""

    def __init__(self, type):
        """
        Tree Initialzation
        """
        if type == 'LOCAL':
            self._type = "local"
        elif type == "HDFS":
            self._type = "hdfs"
        else:
            raise TypeError("Data Type is not local or hdfs type")

        self.base_url = settings.BASETREE_URL or "/dashboard/data/"

    def generate_breadcrumbs(self, path):
        breadcrumbs = [(url_path_join(self.base_url, self._type), '')]
        parts = path.split('/')
        for i in range(len(parts)):
            if parts[i]:
                link = url_path_join(self.base_url, self._type,
                                     url_escape(url_path_join(*parts[:i + 1])),
                                     )
                breadcrumbs.append((link, parts[i]))

        print breadcrumbs

        return breadcrumbs

    def generate_page_title(self, path):
        comps = path.split('/')
        if len(comps) > 3:
            for i in range(len(comps) - 2):
                comps.pop(0)
        page_title = url_path_join(*comps)
        if page_title:
            return page_title + '/'
        else:
            return 'Home'

    def get_tree(self, path=''):
        path = path.strip('/')
        # cm = self.contents_manager
        cm = ContentsManager()

        if cm.dir_exists(path=path):
            if cm.is_hidden(path):

                print "Refusing to serve hidden directory, via 404 Error"

            breadcrumbs = self.generate_breadcrumbs(path)
            page_title = self.generate_page_title(path)

            return page_title, breadcrumbs

        elif cm.file_exists(path):
            # it's not a directory, we have redirecting to do

            # todo
            pass

            # model = cm.get(path, content=False)
            # # redirect to /api/notebooks if it's a notebook, otherwise /api/files
            # service = 'notebooks' if model['type'] == 'notebook' else 'files'
            # url = url_path_join(
            #     self.base_url, service, url_escape(path),
            # )
            # self.log.debug("Redirecting %s to %s", self.request.path, url)
            # self.redirect(url)
        else:
            raise ValueError("404")


class ContentsHandler(object):
    """
    Tree Content Handler
    """

    def __init__(self, type):
        """
        Initialization
        """
        if type == "LOCAL":
            self.contents_manager = FileContentsManager()
        elif type == "HDFS":
            self.contents_manager = HdfsFileContentsManager()
        else:
            raise TypeError("Data Type is not local or hdfs type")

    def get(self, path, request):
        """
        Request Get
        :param request:
        :return:
        """
        type = request.GET.get('type', default=None)
        if type not in {None, 'directory', 'file', 'notebook'}:
            return {
                "status": False,
                "msg": "type error: %s" % (type),
                "code": 4000
            }

        format = request.GET.get('format', default=None)
        if format not in {None, 'text', 'base64'}:
            return {
                "status": False,
                "msg": u'Format %r is invalid' % format,
                "code": 4000
            }

        content = request.GET.get('content', default='1')
        if content not in {'0', '1'}:
            return {
                "status": False,
                "msg": u'Content %r is invalid' % content,
                "code": 4000
            }

        content = int(content)
        result = self.contents_manager.get(
            path=path, type=type, format=format, content=content,
        )

        # if result["status"]:
        #     model = result["data"]
        # else:
        #     return result

        print result

        if result['status'] is True:
            if result['data'].get("type", None) == "directory" and content:
                result['data']['content'].sort(key=sort_key)
            validate_model(result['data'], expect_content=content)

        return {
            "status": True,
            "msg": "Query local data succeed.",
            "data": result
        }




