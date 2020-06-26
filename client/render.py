#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses
from loguru import logger

from genix.common import translate_2to1_util


class NcursesDevice:
    def __init__(self):
        self.screen = None

    def init(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()

    def stop(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def reset(self):
        self.screen.clear()

    def draw(self, buf):
        graphics = "".join(buf)
        self.screen.addstr(graphics)
        self.screen.refresh()


class ConsoleRender:
    def __init__(self, device):
        self.width = 1280
        self.height = 800
        self.scale = 0.8
        self.buffer = []

        self.device = device

    def set_buffer(self, x, y, value):
        idx = translate_2to1_util(x, y, self.width, self.height)
        if idx >= 0 and idx < self.width*self.height:
            self.buffer[idx] = value

    def set_buffer_rel(self, x, y, value, ref_x, ref_y):
        center_x = (self.height - 1) // 2
        center_y = (self.width - 2) // 2

        delta_x, delta_y = ref_x - center_x, ref_y - center_y
        x, y = x - delta_x, y - delta_y
        self.set_buffer(x, y, value)

    def reset_buffer(self):
        term_w, term_h = curses.COLS, curses.LINES

        gw, gh = int(term_w * self.scale) + 1, int(term_h * self.scale)
        gw = gw + 1 if gw % 2 == 1 else gw
        gh = gh + 1 if gh % 2 == 0 else gh

        self.width, self.height = gw, gh
        self.buffer = [" " for i in range(gw * gh)]
        for i in range(gh):
            self.set_buffer(i, gw - 1, "\n")

    def update_boundry(self, boundry_char="x"):
        # fill upper and down boundry
        for i in range(self.width - 1):
            self.set_buffer(0, i, boundry_char)
            self.set_buffer(self.height - 1, i, boundry_char)

        # fill left and right boundry
        for i in range(self.height):
            self.set_buffer(i, 0, boundry_char)
            # -2 because there is an extra newline in every line
            self.set_buffer(i, self.width - 2, boundry_char)

    def update_aoi(self, frame_state):
        # draw current user
        ap = frame_state.ap_state
        #  logger.info(f"current user pos: {(ap.x, ap.y)}")
        self.set_buffer_rel(ap.x, ap.y, ap.avatar, ap.x, ap.y)

        # draw other aoi players
        op_states = frame_state.op_states
        #  logger.info(f"current p: {(ap.x, ap.y)}")
        for op in op_states:
            #  logger.info(f"other p: {(op.x, op.y)}")
            self.set_buffer_rel(op.x, op.y, op.avatar, ap.x, ap.y)

        # draw aoi terrain (current active user is always at the center)
        world_map = frame_state.world_map

        x_start = ap.x - (self.height - 3) // 2
        x_end = ap.x + (self.height - 3) // 2
        y_start = ap.y - (self.width - 4) // 2
        y_end = ap.y + (self.width - 4) // 2

        for i in range(x_start, x_end + 1):
            for j in range(y_start, y_end + 1):
                if (i, j) in world_map:
                    val = str(world_map[(i, j)])
                    self.set_buffer_rel(i, j, val, ap.x, ap.y)

    def update_buffer(self, frame_state):
        self.reset_buffer()
        self.update_boundry()
        self.update_aoi(frame_state)

    def render(self, state):
        self.device.reset()
        self.update_buffer(state)
        self.device.draw(self.buffer)


def test():
    ndevice = NcursesDevice()
    console = ConsoleRender(ndevice)
    state = {}
    console.render(state)
    ndevice.stop()


if __name__ == '__main__':
    test()
