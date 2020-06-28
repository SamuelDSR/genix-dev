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
        return PlayerState.from_dict(pickle.loads(bs))

    @classmethod
    def from_other(self, ps):
        return PlayerState(x=ps.x, y=ps.y, avatar=ps.avatar)


class NetFrame:
    '''Object that reprensets an frame exchange between the client and server
    '''
    def __init__(self, player_state, other_player_states, world_map):
        self.player_state = player_state
        self.other_player_states = other_player_states
        self.world_map = world_map

    @classmethod
    def build_frame(cls, player_state, other_player_states, world_map):
        return pickle.dumps(
            NetFrame(player_state, other_player_states, world_map)
        )

    @classmethod
    def parse_frame(cls, bs):
        return pickle.loads(bs)
