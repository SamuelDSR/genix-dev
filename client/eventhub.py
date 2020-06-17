#!/usr/bin/env python
# -*- coding: utf-8 -*-
from queue import Empty, Queue

from util import Singleton


class CmdQueue(object, metaclass=Singleton):
    def __init__(self):
        self._cmdq = Queue()

    @classmethod
    def get_instance(cls):
        return CmdQueue()

    def get(self, *args, **kwargs):
        return self._cmdq.get(*args, **kwargs)

    def put(self, cmd):
        self._cmdq.put(cmd)
