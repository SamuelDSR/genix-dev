#!/usr/bin/env python
# -*- coding: utf-8 -*-

import attr
from lru import LRU

from genix.common import Singleton, guard_exception, log_exception, PlayerState


class GameState(object, metaclass=Singleton):
    def __init__(self):
        self.is_finished = False
        self.active_player = None
        self.other_players = LRU(10)
        self.world_map = LRU(1000)

    @classmethod
    def get_instance(self):
        return GameState()

    @guard_exception(False)
    @log_exception
    def parse_net_frame(self, net_frame):
        # parse current player
        ap = PlayerState.from_dict(net_frame["active_player"])
        if self.active_player is None:
            self.active_player = ap
        else:
            self.active_player.update(ap)

        # parse other aoi players
        ops = net_frame["other_aoi_players"]
        if len(ops) > self.other_players.get_size():
            self.other_players.set_size(len(ops))

        for op in ops:
            op = PlayerState.from_dict(op)
            if op.name not in self.other_players:
                self.other_players[op.name] = op
            else:
                self.other_players[op.name].update(op)

        # parse world map element
        wm = net_frame["world_map"]
        if len(wm) > self.world_map.get_size():
            self.world_map.set_size(len(wm))
        for item in wm:
            x, y, val = item
            wm[(x, y)] = val

        return True

    def get_update(self, net_frame):
        ret = self.parse_net_frame(net_frame)
        if ret:
            return self
