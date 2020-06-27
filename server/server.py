#!/usr/bin/env py
# -*- coding: utf-8 -*-

import asyncio
import pickle
import time
from queue import Queue
from threading import Lock, Thread

import websockets
from loguru import logger

from genix.common.entity import NetFrame
from genix.common.util import (Singleton, async_guard_exception,
                               async_log_exception, guard_exception,
                               log_exception, popall, await_with_timeout)
from genix.server.entity import WorldMap
from genix.server.handler import UserCmdHandler
from genix.server.db import GenixDB


class GameServer(object, metaclass=Singleton):
    def __init__(self,
                 host,
                 port,
                 hz=20,
                 datapath="/home/samuel_vita/Documents/genix-dev/genix/data",
                 debug=True):
        self.host = host
        self.port = port
        self.datapath = datapath
        self.debug = debug

        self.active_users = {}

        self.loop = asyncio.get_event_loop()
        self.lock = Lock()

        self.tick_time = 1.0 / hz
        self.ticks = 0

        self.cmdq = Queue()
        self.cmd_handler = UserCmdHandler()

        self.world_map = WorldMap().load(f'{self.datapath}/world_map.pkl')

        self.init_database()

    @property
    def world_width(self):
        return self.world_map.width

    @property
    def world_height(self):
        return self.world_map.height

    def get_player(self, socket):
        return self.active_users.get(socket, None)

    def add_player(self, socket, player):
        self.active_users[socket] = player

    async def del_player(self, socket):
        await self.db.update_user(self.get_player(socket))
        if socket in self.active_users:
            del self.active_users[socket]

    def has_player(self, socket):
        return socket in self.active_users

    @classmethod
    def get_instance(cls):
        return GameServer()

    def init_database(self):
        self.db = GenixDB(f'sqlite:///{self.datapath}/genix.db', self.debug)
        self.loop.run_until_complete(self.db.connect())

    def is_legal(self, x, y, player):
        if x < 0 or x >= self.world_height or\
                y < 0 or y >= self.world_width or\
                (x, y) in self.world_map:
            return False

        # check user collide
        for p in self.active_users.values():
            if p != player and p.state.x == x and p.state.y == y:
                return False
        return True

    @async_guard_exception(None)
    @async_log_exception
    async def player_connect(self, socket, path):
        """
        Handle user connection, it send back a msg to client which
        indicates either an success or error
        msg:
            -1: invalid login|register requests
            -2: invalid login user|password
            -3: invalid register password
            0 : login success
            1 : register success
        Args:
            socket:
            path:

        Returns:
            None
        """
        # parse login requests
        tokens = pickle.loads(await socket.recv())
        try:
            action, username, password = tokens["action"], tokens[
                "username"], tokens["password"]
        except Exception:
            if self.debug:
                logger.error(f"Server: unvalid user connect request: {tokens}")
            await socket.send(pickle.dumps(-1))
            return

        player = None
        if action == "login":
            player = await self.db.restore_user(username, password)
            await socket.send(pickle.dumps(0 if player else -2))

        elif action == "register":
            player = await self.db.register_user(username, password, 90, 90)
            await socket.send(pickle.dumps(1 if player else -3))
        else:
            pass

        if player:
            self.add_player(socket, player)
            logger.info("Player Connection finished")

    @async_guard_exception(None)
    @async_log_exception
    async def player_step(self, socket):
        player = self.active_users[socket]
        await socket.send(player.frames.get())

        # recieve client updates
        #  cmds = await self.await_with_timeout(websocket.recv(), 0.05, None)
        cmds = await socket.recv()
        if cmds is not None:
            cmds = pickle.loads(cmds)
            #  logger.info(f"Server: received cmds from client {cmds}")
            for c in cmds:
                self.cmdq.put_nowait((socket, c))

    async def player_connection(self, socket, path):
        while not self.has_player(socket):
            # if player terminate connection before login, must return
            if socket.closed:
                logger.info("woops, socket closed")
                return
            await self.player_connect(socket, path)

        if self.debug:
            logger.info("User connection finished")

        while self.has_player(socket):
            if socket.closed:
                await self.del_player(socket)
                return
            await self.player_step(socket)

    def process_player_cmds(self, cmds_to_exe):
        self.cmd_handler.execute(self, cmds_to_exe)

    def update_players(self):
        for _, player in self.active_users.items():
            state = player.state
            other_states = [p.state for p in self.active_users.values() if p != player]
            map_slice = self.world_map.get_slice(state.x, state.y, 200, 200)
            player.frames.put_nowait(
                NetFrame.build_frame(state, other_states, map_slice))
            #  logger.info(f"Update frame {player.username} succeed")

    @guard_exception(None)
    @log_exception
    def lock_step(self):
        cmds_to_exe = popall(self.cmdq)

        #  if self.debug and len(cmds_to_exe) > 0:
            #  logger.info(f"Get {len(cmds_to_exe)} to process in lock step")

        self.process_player_cmds(cmds_to_exe)

        self.update_players()

    def start_ticker(self):
        def _target():
            server_beginning_ts = time.time()
            while True:
                tick_beginning = time.time()
                # step
                self.lock_step()

                now = time.time()
                delta = self.tick_time - (now - tick_beginning)
                if delta > 0:
                    time.sleep(delta)

                self.ticks += 1
                if self.ticks % 120 == 0:
                    tick_rate = self.ticks / (time.time() - server_beginning_ts)
                    logger.info(f"tick rate: {tick_rate} FPS")

        self.ticker = Thread(target=_target)
        self.ticker.start()

    def start(self):
        self.start_ticker()
        tcp_server = websockets.serve(self.player_connection, self.host, self.port)
        self.loop.run_until_complete(tcp_server)
        self.loop.run_forever()


if __name__ == '__main__':
    host, port = "127.0.0.1", 12345
    game_server = GameServer(host, port, hz=15)
    game_server.start()
