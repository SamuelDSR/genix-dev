#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import pickle
import time
from queue import Queue
from threading import Lock, Thread

import stdiomask
import websockets
from loguru import logger
from pynput.keyboard import Listener

from genix.client.render import ConsoleRender, NcursesDevice
from genix.client.state import GameState
from genix.common.entity import NetFrame
from genix.common.util import (Singleton, await_with_timeout, init_logger,
                               key_repr, popall)

ALL_VALID_KEYS = set(
    ["ctrl", "ctrl-r", "up", "left", "right", "down", "j", "k", "l", "h"])


class GameClient(object, metaclass=Singleton):
    def __init__(self, host, port, hz=24):
        self.state = GameState()
        self.cmd_queue = Queue()
        self.net_queue = Queue()
        self.lock = Lock()
        self.loop = asyncio.get_event_loop()
        self.socket = None
        self.host = host
        self.port = port
        self.tick_time = 1.0 / hz
        self.uri = f"ws://{host}:{port}"
        self.login = False

        self.device = NcursesDevice()
        self.render = ConsoleRender(self.device)

        self.rs = 0
        self.ns = 0

    @classmethod
    def get_instance(cls):
        return GameClient()

    def start(self):
        try:
            init_logger("/home/samuel_vita/Documents/genix-dev/client.log")
            self.loop.run_until_complete(self.connect())
            self.start_input_listener()
            self.start_render()
            self.start_network()
        except Exception:
            pass
        finally:
            self.device.stop()

    def start_render(self):
        def _target():
            self.device.init()

            # start rendering game ui
            while True:
                start = time.time()

                # get latest game state update
                try:
                    bs = self.net_queue.get()
                    net_frame = NetFrame.parse_frame(bs)

                    self.rs += 1
                    if self.rs % 10 == 0:
                        logger.info(f"get render frame: {self.rs}")

                    self.render.render(net_frame)
                except Exception as e:
                    print(e)

                end = time.time()
                delta = self.tick_time - (end - start)
                if delta > 0:
                    #  logger.info(f"Render extra sleep {delta}")
                    time.sleep(delta)

            self.device.stop()

        self.ui_thread = Thread(target=_target)
        self.ui_thread.start()

    def start_input_listener(self):
        def on_press(key):
            k = key_repr(key)
            if k in ALL_VALID_KEYS:
                self.cmd_queue.put_nowait((k, "p"))

        def on_release(key):
            k = key_repr(key)
            if k in ALL_VALID_KEYS:
                self.cmd_queue.put_nowait((k, "r"))

        self.input_thread = Listener(on_press=on_press, on_release=on_release)
        self.input_thread.start()

    def start_network(self):
        self.loop.run_until_complete(self.handle_connection())

    def login_ui(self):
        action = input("Login[L|l]/Register[R|r]: ")
        while action not in "LlRr":
            print("Please chose between login|register")
            action = input("Login[L|l]/Register[R|r]: ")

        action = "register" if action in "rR" else "login"
        username = input("Username: ")
        password = stdiomask.getpass()
        return action, username, password

    async def connect(self):
        print("==========================Genix===============================")
        print("=============Please login/register first======================")
        socket = await websockets.connect(self.uri)
        success = False
        while not success:
            if socket.closed:
                socket = await websockets.connect(self.uri)
            action, username, password = self.login_ui()
            requests = {
                "action": action,
                "username": username,
                "password": password
            }
            try:
                await socket.send(pickle.dumps(requests))
                flag = pickle.loads(await socket.recv())
                if flag >= 0:
                    success = True
                else:
                    print(
                        "=============================================================="
                    )
                    if flag == -1:
                        print("Invalid login requests, please check")
                    elif flag == -2:
                        print("Invalid username/password")
                    elif flag == -3:
                        print(
                            "Password is too short|long (must between 5-15 characters)"
                        )
                    else:
                        pass
                    print(
                        "=============================================================="
                    )
            except Exception:
                continue

        print("Login|Register succeed")
        # notify ui thread
        with self.lock:
            self.login = True
        self.socket = socket

    async def handle_connection(self):
        while True:
            bs = await self.socket.recv()
            self.net_queue.put_nowait(bs)
            self.ns += 1
            if self.ns % 10 == 0:
                logger.info(f"get net frame: {self.ns}")
            cmds = popall(self.cmd_queue)
            await self.socket.send(pickle.dumps(cmds))


if __name__ == '__main__':
    import sys
    host, port = "127.0.0.1", 12345
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = sys.argv[2]
    client = GameClient(host, port, hz=20)
    try:
        client.start()
    except Exception:
        pass
    finally:
        client.device.stop()
