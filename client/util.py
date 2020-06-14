#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil

from loguru import logger


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_terminal_size():
    size = shutil.get_terminal_size()
    return size.columns, size.lines


def translate_2to1_util(i, j, grid_w, grid_h):
    if i >= 0 and i < grid_h and j >= 0 and j < grid_w:
        return i * grid_w + j
    raise ValueError(
        f"2D coords ({i}, {j}) out of ({grid_w}, {grid_h}) boundry")


def initLogger():
    logger.remove()
    logger.add("genix-client.log", format="{time} {level} {message}", level="INFO")


def clear_stdout():
    os.system("clear")
