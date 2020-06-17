#!/usr/bin/env python
# -*- coding: utf-8 -*-

from eventhandler import KeyboardHandler

def update_state():
    keyboard_handler = KeyboardHandler.get_instance()
    keyboard_handler.execute()


def game_tick_udate():
    pass
