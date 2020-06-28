#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
from queue import Queue
from loguru import logger

from genix.common.entity import PlayerState
from genix.common.util import generate_random_grid


class Player:
    def __init__(
            self,
            username,
            state,
            gs=None,
    ):
        self.state = state
        self.username = username
        self.frames = Queue()


class WorldMap:
    def __init__(self, data=None, width=None, height=None):
        self._data = data
        self._width = width
        self._height = height

    @classmethod
    def regenerate(cls, width, height, ratio, max_size, art_props):
        arts, props = generate_random_grid(width, height, ratio, max_size,
                                           art_props)
        data = {}
        for art, prop in zip(arts, props):
            for coord in art:
                data[coord] = prop
        return WorldMap(data, width, height)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def __contains__(self, item):
        return item in self._data

    def __getitem__(self, key):
        return self._data.get(key, None)

    def __setitem__(self, key, val):
        self._data[key] = val

    def __delitem__(self, key):
        del self._data[key]

    def __len__(self):
        return self.width * self.height

    def __iter__(self):
        return iter(self._data)

    def get_slice(self, cx, cy, w, h):
        _map = {}
        for i in range(cx - w // 2, cx + w // 2):
            for j in range(cy - h // 2, cy + h // 2):
                if (i, j) in self._data:
                    _map[(i, j)] = self._data[(i, j)]
        return _map

    def has(self, key):
        return key in self._data

    def load(self, path):
        with open(path, 'rb') as f:
            obj = pickle.load(f)
            return WorldMap(obj["_data"], obj["_width"], obj["_height"])

    def dump(self, path):
        with open(path, 'wb') as f:
            obj = {}
            obj["_data"] = self._data
            obj["_width"] = self._width
            obj["_height"] = self._height
            pickle.dump(obj, f)


def test_generate_wm():
    wm = WorldMap.regenerate(1000, 1000, 0.08, 50, range(10))
    wm.dump("genix/data/world_map.pkl")


def test_load_wm():
    wm = WorldMap().load("genix/data/world_map.pkl")
    print(wm.width)
    print(wm.height)
    print(wm.has((100, 100)))
    print(wm.get_slice(100, 100, 20, 20))
    print(wm[(50, 100)])


if __name__ == '__main__':
    #  test_generate_wm()
    test_load_wm()
