#!/usr/bin/env python
# -*- coding: utf-8 -*-

from eventhandler import get_keyboard_listener
from cmd import KeyboardHandler
from util import initLogger
import os

import time

#  os.system('stty -echo')
print("Hello")
initLogger()

listener = get_keyboard_listener()
listener.start()

handler = KeyboardHandler()
while True:
    handler.execute()
    time.sleep(0.5)

print("Job finished")
#  os.system('stty echo')
