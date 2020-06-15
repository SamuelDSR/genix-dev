#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
import random
import itertools
import time

from loguru import logger


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_terminal_size():
    size = shutil.get_terminal_size()
    return size.columns, size.lines


def translate_2to1_util(i, j, grid_w, grid_h):
    if i >= 0 and i < grid_h and j >= 0 and j < grid_w:
        return i * grid_w + j
    raise ValueError(
        f"2D coords ({i}, {j}) out of ({grid_w}, {grid_h}) boundry")


def init_logger():
    logger.remove()
    logger.add("genix-client.log",
               format="{time} {level} {message}",
               level="INFO")


def generate_random_grid(width, height, ratio, maxsize, art_props):
    start = time.time()

    articles = []
    article_props = []
    article_demand_sizes = []

    max_capacity = int(width*height*ratio)
    occupied_points = set()

    def _random_until_satisfied(max_tries):
        i = 0
        while i <= max_tries:
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            if (x, y) not in occupied_points:
                return (x, y)
            i += 1

    def _inside_grid(x, y):
        return x >= 0 and x < width and y >= 0 and y < height


    def _shape_constraint(x, y, min_x, max_x, min_y, max_y, max_area):
        _min_x = min(x, min_x)
        _max_x = max(x, max_x)
        _min_y = min(y, min_y)
        _max_y = max(y, max_y)
        if (_max_x - _min_x)*(_max_y - _min_y) <= max_area:
            return True, _min_x, _max_x, _min_y, _max_y
        return False, min_x, max_x, min_y, max_y


    GROW_DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    #  GROW_DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    while max_capacity > 0:

        art_size = random.randint(1, min(max_capacity, maxsize))
        #  print(f"demanded art size {art_size}")

        article_demand_sizes.append(art_size)
        article_props.append(random.choice(art_props))

        # prevent single grow at arbitary shape
        # the are of min rect that contains the shape must not exceed this art_boundry
        art_boundry = art_size*4

        # create one connected article
        art = []
        art_min_x = width - 1
        art_max_x = 0
        art_min_y = height - 1
        art_max_y = 0

        art_tries = 0
        while len(art) < art_size:
            art_tries += 1
            if art_tries > art_size+1:
                break

            if len(art) == 0:
                # try at least 2*current capacity
                p = _random_until_satisfied(max_capacity*2)
                if p:
                    occupied_points.add(p)
                    art.append(p)
                    #  print(f"get start point {p}")
                else:
                    #  print("oops, cannot even find an start point")
                    break
            else:
                tries = 0
                random.shuffle(GROW_DIRS)
                for delta in itertools.cycle(GROW_DIRS):
                    tries += 1
                    if tries > len(art)*2 + 8:
                    #  if tries > 10:
                        break

                    extended_p = random.choice(art)
                    new_x = extended_p[0] + delta[0]
                    new_y = extended_p[1] + delta[1]
                    is_constrained, art_min_x, art_max_x, art_min_y, art_max_y = _shape_constraint(
                        new_x, new_y, art_min_x, art_max_x, art_min_y, art_max_y, art_boundry
                    )
                    if _inside_grid(new_x, new_y) and ((new_x, new_y) not in occupied_points) and is_constrained:
                        occupied_points.add((new_x, new_y))
                        old_art_size = len(art)
                        art.append((new_x, new_y))
                        break

        if len(art) > 0:
            articles.append(art)
            max_capacity -= len(art)

    return articles, article_props
