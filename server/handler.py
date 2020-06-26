#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict

from loguru import logger
from genix.common.util import Singleton


class KeyboardUpCmd:
    @classmethod
    def execute(cls, gs, player):
        #  logger.info("Keyboard Up Execute")
        #  logger.info(f"before: {player.X}")
        player.X -= 1
        #  logger.info(f"after: {player.X}")


class KeyboardDownCmd:
    @classmethod
    def execute(cls, gs, player):
        #  logger.info("Keyboard Down Execute")
        #  logger.info(f"before: {player.X}")
        player.X += 1
        #  logger.info(f"after: {player.X}")


class KeyboardLeftCmd:
    @classmethod
    def execute(cls, gs, player):
        #  logger.info("Keyboard Left Execute")
        #  logger.info(f"before: {player.Y}")
        player.Y -= 1
        #  logger.info(f"after: {player.Y}")


class KeyboardRightCmd:
    @classmethod
    def execute(cls, gs, player):
        #  logger.info("Keyboard Right Execute")
        #  logger.info(f"before: {player.Y}")
        player.Y += 1
        #  logger.info(f"after: {player.Y}")


VALID_KEY_COMBS = dict([('up', KeyboardUpCmd),
                        ('down', KeyboardDownCmd),
                        ('left', KeyboardLeftCmd),
                        ('right', KeyboardRightCmd),
                        ('j', KeyboardDownCmd),
                        ('h', KeyboardLeftCmd),
                        ('l', KeyboardRightCmd),
                        ('k', KeyboardUpCmd)])


VALID_SPEC_KEY = set(["ctrl", "ctrl-r", "shift", "shift-r", "alt", "alt-r"])


class UserCmdHandler(object, metaclass=Singleton):
    def __init__(self):
        self.special_keys = defaultdict(set)

    @classmethod
    def get_instance(cls):
        return UserCmdHandler()

    def get_combined_key(self, websocket, key):
        spec_keys = self.special_keys[websocket]
        if len(spec_keys) == 0:
            return None

        comb_key = "+".join([k for k in sorted(spec_keys)])
        comb_key = comb_key + "+" + key
        logger.info(f"Get combined keys: {comb_key}")
        return comb_key

    def yield_execute_unit(self, gs, user_cmds):
        socket, (key, action) = user_cmds.popleft()
        #  logger.info(f"get {key, action} from user cmd queue")
        player = gs.active_users[socket]

        valid_cmd = None
        if action == "p":
            if key in VALID_SPEC_KEY:
                self.special_keys[socket].add(key)
            else:
                # get all combined keys
                comb_key = self.get_combined_key(socket, key)

                # priority for combinations keystrokes
                if comb_key and comb_key in VALID_KEY_COMBS:
                    valid_cmd = VALID_KEY_COMBS[comb_key]
                # then check key alone
                elif key in VALID_KEY_COMBS:
                    valid_cmd = VALID_KEY_COMBS[key]
                else:
                    pass
        else:
            # remove special key when it is released
            if key in VALID_SPEC_KEY and key in self.special_keys[socket]:
                self.special_keys[socket].remove(key)

        return player, valid_cmd

    def execute(self, gs, user_cmds):
        while len(user_cmds) > 0:
            player, cmd = self.yield_execute_unit(gs, user_cmds)
            if cmd is not None:
                cmd.execute(gs, player)
