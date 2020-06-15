#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from util import Singleton, translate_2to1_util


class GameState(object, metaclass=Singleton):
    def __init__(self):
        self.is_finished = False

        self.game_grid = []
        self.game_width = sys.maxsize
        self.game_height = sys.maxsize
        self.game_scale = 0.8

        self.world_width = 500
        self.world_height = 500
        self.world_grid = {}
        self.world_ratio = 0.1

        self.active_player = None

    @classmethod
    def get_instance(self):
        return GameState()

    def set_world(self, x, y, value):
        self.world_grid[(x, y)] = value

    def set_player(self, p):
        self.active_player = p

    def set_game_grid(self, x, y, value):
        idx = translate_2to1_util(x, y, self.game_width, self.game_height)
        self.game_grid[idx] = value

    def set_game_grid_by_world_coords(self, x, y, value):
        grid_x, grid_y = (self.game_height - 1) // 2, (self.game_width -
                                                       2) // 2
        delta_x, delta_y = self.active_player.X - grid_x, self.active_player.Y - grid_y
        grid_x, grid_y = x - delta_x, y - delta_y
        self.set_game_grid(grid_x, grid_y, value)

    def render_map(self, other_aoi_player):
        #  global GameGrid, ActivePlayer, WorldGrid, GameHeight, GameWidth
        #  GameGrid[translate_world_2to1(ActivePlayer.X,
        #  ActivePlayer.Y)] = ActivePlayer.name

        # render active player
        self.set_game_grid_by_world_coords(self.active_player.X,
                                           self.active_player.Y,
                                           self.active_player.name)

        # render other aoi player
        for p in other_aoi_player:
            self.set_game_grid_by_world_coords(p.X, p.Y, p.name)
            #  GameGrid[translate_world_2to1(p.X, p.Y)] = p.name

        # render terrain
        x_start = self.active_player.X - (self.game_height - 3) // 2
        x_end = self.active_player.X + (self.game_height - 3) // 2

        y_start = self.active_player.Y - (self.game_width - 4) // 2
        y_end = self.active_player.Y + (self.game_width - 4) // 2


        for i in range(x_start, x_end + 1):
            for j in range(y_start, y_end + 1):
                if (i, j) in self.world_grid:
                    self.set_game_grid_by_world_coords(
                        i, j, str(self.world_grid[(i, j)]))
                    #  GameGrid[translate_world_2to1(i, j)] = str(WorldGrid[(i, j)])

    def render_boundry(self, boundry_char="x"):

        # fill upper and down boundry
        for i in range(self.game_width - 1):
            self.set_game_grid(0, i, boundry_char)
            self.set_game_grid(self.game_height - 1, i, boundry_char)

            #  GameGrid[translate_2to1(0, i)] = boundry_char
            #  GameGrid[translate_2to1(GameHeight - 1, i)] = boundry_char

        # fill left and right boundry
        for i in range(self.game_height):
            self.set_game_grid(i, 0, boundry_char)
            self.set_game_grid(i, self.game_width - 2, boundry_char)

            #  GameGrid[translate_2to1(i, 0)] = boundry_char
            #  GameGrid[translate_2to1(i, GameWidth - 2)] = boundry_char
