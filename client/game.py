import curses
import random
import sys
import time

from event import init_listener
from logic import update_state
from player import Player
from state import GameState
from util import generate_random_grid, init_logger

gs = GameState.get_instance()


def init_world():
    coords, terrain_type = generate_random_grid(gs.world_width,
                                                gs.world_height,
                                                gs.world_ratio, 80,
                                                range(1, 10))
    for article, t in zip(coords, terrain_type):
        for x, y in article:
            gs.set_world(x, y, t)


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


def init_view_device():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    return stdscr


def stop_view_device():
    curses.nocbreak()
    curses.echo()
    curses.endwin()


def reset_grid(stdscr):
    term_w, term_h = curses.COLS, curses.LINES

    gw, gh = int(term_w * gs.game_scale) + 1, int(term_h * gs.game_scale)
    gw = gw + 1 if gw % 2 == 1 else gw
    gh = gh + 1 if gh % 2 == 0 else gh

    gs.game_width, gs.game_height = gw, gh
    gs.game_grid = [" " for i in range(gw * gh)]
    for i in range(gh):
        gs.set_game_grid(i, gw - 1, "\n")


def render(stdscr):
    stdscr.clear()

    reset_grid(stdscr)

    gs.render_boundry()
    gs.render_map([])

    # start real rendering
    stdscr.addstr("".join(gs.game_grid))
    stdscr.refresh()


def run():
    # initialize game
    init_logger()
    init_world()
    init_player()
    init_listener()
    stdscr = init_view_device()

    # main loop
    while not gs.is_finished:
        update_state()
        render(stdscr)
        time.sleep(1 / 12)


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print(e)
        print(sys.exec_info())
        print("failed")
    finally:
        stop_view_device()
