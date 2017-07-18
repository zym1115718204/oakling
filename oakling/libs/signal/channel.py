#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-06-08 07:21:34
#  plugin

import json


class Channel(object):
    """
    Channel connect  to websocket
    """
    def __init__(self, _channel):
        """
        :param channel: websocket Handler
        """
        self._channel = _channel

    def log(self, log):
        """
        :param log:
        """
        if self._channel:
            _log = {
                "client_id": self._channel.client_id,
                "name": "demo2",
                "signal": "run",
                "data": log,
            }
            self._channel.update_cache(json.dumps(_log))
            self._channel.write_message(json.dumps(_log))

        else:
            print "Channel unavailable"

    def prograss(self, prograss):
        """
        :param prograss:
        :return:
        """
        if self._channel:
            _log = {
                "client_id": self._channel.client_id,
                "name": "demo2",
                "signal": "run",
                "data": {
                    "prograss": prograss
                },
            }
            self._channel.update_cache(json.dumps(_log))
            self._channel.write_message(json.dumps(_log))

        else:
            print "Channel unavailable"
