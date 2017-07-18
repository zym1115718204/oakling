# -*- encoding:utf-8 -*-
# 2014-12-18
# author: orangleliu

from __future__ import absolute_import

import os
import time
import json
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.escape
import logging

import uuid


logger = logging.getLogger('fib')

logger.setLevel(logging.INFO)

hdr = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
hdr.setFormatter(formatter)

logger.addHandler(hdr)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oakling.settings")

from django.conf import settings
from collector.handler import Handler


class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', messages=WebSocketHandler.cache)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    client_id = 1
    debugers = set()
    admins = set()
    cache = []
    cache_size = 20
    activate = settings.BASE_DIR

    @classmethod
    def update_cache(cls, debug_message):
        """
        Store cache
        :param debugers:
        :return:
        """
        cls.cache.append(debug_message)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    def check_origin(self, origin):
        return True

    def open(self):
        logger.info("got new connection ")
        self.client_id = WebSocketHandler.client_id
        WebSocketHandler.client_id = WebSocketHandler.client_id + 1
        WebSocketHandler.debugers.add(self)
        pass

    def on_close(self):
        WebSocketHandler.debugers.remove(self)

    def on_message(self, message):

        logger.info("got meassage %r", message)

        parsed = tornado.escape.json_decode(message)

        def _package(project_name, signal, data):
            """
            Package send message
            :param name: project name
            :param signal: signal
            :param data: data
            :return: message dict
            """
            return {
                "client_id": self.client_id,
                "name": project_name,
                "signal": signal,
                "data": data,
            }

        def _send(msg):
            """
            Send packaged message to client
            :param msg:
            :return:
            """
            if self.admin:
                WebSocketHandler.update_cache(json.dumps(msg))
                WebSocketHandler.send_updates(json.dumps(msg))
            else:
                WebSocketHandler.update_cache(json.dumps(msg))
                self.write_message(json.dumps(msg))

        name = parsed.get("name", None)
        command = parsed.get("command", False)
        signal = parsed.get("signal", None)
        data = parsed.get("data", None)
        self.admin = parsed.get("admin", False)

        if name and command and signal == "run":
            _send(_package(name, signal, "Start running"))
            handler = Handler()
            # i = 0
            # while i <= 100:
            #     data = {
            #         "prograss": i,
            #     }
            #     _send(_package(name, signal, data))
            #     _send(_package(name, signal, data))
            #     time.sleep(0.1)
            #     i += 10

            result = handler.run_once_processor(name, self)

            _send(_package(name, signal, result))
            _send(_package(name, signal, "Stop running"))

        elif name and command and signal == "info":
            _send(_package(name, signal, data))

        else:
            result = {
                "status": False,
                "project": name,
                "message": "Bad Parameters",
                "code": 4001,
            }
            _send(_package(name, signal, result))
            _send(_package(name, signal, "Stop running"))

        # WebSocketHandler.update_cache(json.dumps(info))
        # self.write_message(json.dumps(info))

    @classmethod
    def send_updates(cls, debug_message):
        """
        Send update message
        :param debug_message:
        :return:
        """

        logger.info("Sending message to debuger")
        for debuger in cls.debugers:
            print "##################", debuger
            print "##################", debuger.client_id
            try:
                debuger.write_message(debug_message)
            except:
                logger.error("Error sending message", exc_info=True)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexPageHandler),
            (r'/ws', WebSocketHandler)
        ]

        settings = {"template_path": "."}
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
