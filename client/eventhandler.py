#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from queue import Empty, Queue

from loguru import logger
from pynput import keyboard

from eventhub import CmdQueue
from state import GameState
from util import Singleton

gs = GameState.get_instance()


class Cmd:
    def execute(self):
        pass


class KeyboardUpCmd(Cmd):
    def execute(self):
        logger.info("Keyboard Up Execute")
        gs.active_player.X -= 1


class KeyboardDownCmd(Cmd):
    def execute(self):
        logger.info("Keyboard Down Execute")
        gs.active_player.X += 1


class KeyboardLeftCmd(Cmd):
    def execute(self):
        logger.info("Keyboard Left Execute")
        gs.active_player.Y -= 1


class KeyboardRightCmd(Cmd):
    def execute(self):
        logger.info("Keyboard Right Execute")
        gs.active_player.Y += 1


class KeyboardEscCmd(Cmd):
    def execute(self):
        logger.info("Keyboard Esc Execute")
        gs.is_finished = True


class KeyboardHandler(object, metaclass=Singleton):

    VALID_KEY_COMBS = dict([('up', KeyboardUpCmd), ('down', KeyboardDownCmd),
                            ('left', KeyboardLeftCmd),
                            ('right', KeyboardRightCmd),
                            ('x', KeyboardEscCmd)])

    VALID_SPEC_KEY = set(
        ["ctrl", "ctrl-r", "shift", "shift-r", "alt", "alt-r", "esc"])

    def __init__(self):
        self._cq = CmdQueue()
        self._cmds = deque([])
        self._valid_cmd = None
        self._special_keys = set()

    @classmethod
    def get_instance(cls):
        return KeyboardHandler()

    def get_combined_key(self, key):
        if len(self._special_keys) == 0:
            return None
        comb_key = "+".join([k for k in sorted(self._special_keys)])
        comb_key = comb_key + "+" + key
        logger.info(f"Get combined keys: {comb_key}")
        return comb_key

    @classmethod
    def get_key_repr(cls, key):
        if isinstance(key, keyboard.Key):
            return key.name
        elif isinstance(key, keyboard.KeyCode):
            return key.char
        else:
            logger.warning(f"Unknown key pressed {key}")
            return ""

    def yield_valid_cmd(self):
        if len(self._cmds) == 0:
            return

        key, action = self._cmds.popleft()
        key = KeyboardHandler.get_key_repr(key)

        if action == "p":
            if key in KeyboardHandler.VALID_SPEC_KEY:
                self._special_keys.add(key)
            else:
                # get all combined keys
                comb_key = self.get_combined_key(key)

                # priority for combinations keystrokes
                if comb_key and comb_key in KeyboardHandler.VALID_KEY_COMBS:
                    self._valid_cmd = KeyboardHandler.VALID_KEY_COMBS[
                        comb_key]()
                # then check key alone
                elif key in KeyboardHandler.VALID_KEY_COMBS:
                    self._valid_cmd = KeyboardHandler.VALID_KEY_COMBS[key]()
                else:
                    pass
        else:
            # remove special key when it is released
            if key in KeyboardHandler.VALID_SPEC_KEY and key in self._special_keys:
                self._special_keys.remove(key)

    def execute(self):
        while True:
            try:
                self._cmds.append(self._cq.get(block=False))
            except Empty as e:
                break

        while len(self._cmds) > 0:
            self.yield_valid_cmd()
            if self._valid_cmd:
                self._valid_cmd.execute()
                self._valid_cmd = None
