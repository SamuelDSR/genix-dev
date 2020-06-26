# -*- coding: utf-8 -*-

from enum import Enum, auto

import attr
import pickle


class Element(Enum):

    METAL = auto()
    WOOD = auto()
    WATER = auto()
    FIRE = auto()
    EARTH = auto()


@attr.s
class PlayerState:

    x = attr.ib()
    y = attr.ib()
    avatar = attr.ib()

    def update(self, ps):
        self.x = ps.x
        self.y = ps.y
        self.avatar = ps.avatar

    @classmethod
    def from_dict(self, d):
        return PlayerState(x=d['x'], y=d['y'], avatar=d['avatar'])

    def to_binary(self):
        return pickle.dumps(self.__dict__)

    @classmethod
    def from_binary(self, bs):
        return PlayerState.from_dict(
            pickle.loads(bs)
        )



class NetFrame:
    '''Object that reprensets an frame exchange between the client and server
    '''

    def __init__(self, ap_state, op_states, world_map):
        self.ap_state = ap_state
        self.op_states = op_states
        self.world_map = world_map


    def __str__(self):
        return f"Active Player: {self.ap_state}, WorldMap: {self.world_map}"
