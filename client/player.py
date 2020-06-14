#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Player:

    def __init__(self, name, x=0, y=0, game_state=None):
        self._x = x
        self._y = y
        self.name = name
        self._gs = game_state

    @property
    def X(self):
        return self._x

    @X.setter
    def X(self, value):
        if self.is_legal(value, self._y):
            self._x = value

    @property
    def Y(self):
        return self._y

    @Y.setter
    def Y(self, value):
        if self.is_legal(self._x, value):
            self._y = value

    def is_legal(self, x, y):
        if x < 0 or x >= self._gs.world_height or y < 0 or y >= self._gs.world_width or\
                (x, y) in self._gs.world_grid:
            return False
        return True
