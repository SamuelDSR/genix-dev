import os
import random
import sys
import time

from player import Player
from state import GameState
from util import get_terminal_size, initLogger, clear_stdout
from cmd import KeyboardHandler
from eventhandler import get_keyboard_listener

gs = GameState.get_instance()
handler = KeyboardHandler.get_instance()


def init_world():
    terrain_size = gs.get_terrain_size()
    terrain_xs = [
        random.randint(0, gs.world_width - 1) for i in range(terrain_size)
    ]
    terrain_ys = [
        random.randint(0, gs.world_height - 1) for i in range(terrain_size)
    ]
    for x, y in zip(terrain_xs, terrain_ys):
        gs.set_world(x, y, random.randint(1, 9))

    #  print(gs.world_grid)


def init_player():
    world_width, world_height = gs.world_width, gs.world_height
    world_grid = gs.world_grid

    x, y = random.randint(0, world_width - 1), random.randint(
        0, world_height - 1)

    while (x, y) in world_grid:
        x, y = random.randint(0, world_width - 1), random.randint(
            0, world_height - 1)

    gs.set_player(Player(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), x, y,
                         gs))


def init_listener():
    listener = get_keyboard_listener()
    listener.start()


def init_game():
    initLogger()
    init_world()
    init_player()
    init_listener()


def update_state():
    handler.execute()


def run():
    #  os.system("clear")
    init_game()
    while not gs.is_finished:
        update_state()
        render()
        time.sleep(1/10)


def flush_grid():
    os.system("clear")
    term_w, term_h = get_terminal_size()

    #  print(f"terminal size: {(term_w, term_h)}")
    gw, gh = int(term_w * gs.game_scale) + 1, int(term_h * gs.game_scale)
    gw = gw + 1 if gw % 2 == 1 else gw
    gh = gh + 1 if gh % 2 == 0 else gh
    #  print(f"Game grid size: ({gw}, {gh})")
    #  term not changed, reuse grid data
    #  if gw != gs.game_width or gh != gs.game_height:
    gs.game_width, gs.game_height = gw, gh
    gs.game_grid = [" " for i in range(gw * gh)]
    for i in range(gh):
        gs.set_game_grid(i, gw - 1, "\n")


def render():
    flush_grid()
    gs.render_boundry()
    gs.render_map([])

    # start real rendering
    sys.stdout.write("".join(gs.game_grid))
    sys.stdout.flush()


if __name__ == '__main__':
    run()
