#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pynput.keyboard import Key, Listener
from cmd import CmdQueue


def get_keyboard_listener():
    cmdq = CmdQueue.get_instance()

    def on_press(key):
        cmdq.put((key, "p"))

    def on_release(key):
        cmdq.put((key, "r"))

    return Listener(on_press=on_press, on_release=on_release)
