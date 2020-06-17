#!/usr/bin/env python
# -*- coding: utf-8 -*-

from event import get_keyboard_listener
from eventhandler import KeyboardHandler
from util import init_logger
import os

import time

#  os.system('stty -echo')
#  print("Hello")
#  init_logger()
#
#  listener = get_keyboard_listener()
#  listener.start()
#
#  handler = KeyboardHandler()
#  while True:
    #  handler.execute()
    #  time.sleep(0.5)
#
#  print("Job finished")
#  os.system('stty echo')

from util import generate_random_grid

arts, art_sizes = generate_random_grid(500, 500, 0.15, 50, [1,2,3,4,5])
#  print(arts)
print(art_sizes)
