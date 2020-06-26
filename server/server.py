#!/usr/bin/env py
# -*- coding: utf-8 -*-

import asyncio
import hashlib
import pickle
import time
from collections import deque
from queue import Empty, Queue
from threading import Lock, Thread

import sqlalchemy
import websockets
from async_timeout import timeout
from databases import Database
from loguru import logger

from genix.common.util import (Singleton, async_guard_exception,
                               async_log_exception, guard_exception,
                               log_exception)
from genix.server.entity import Player, WorldMap
from genix.common.entity import PlayerState, NetFrame
from genix.server.handler import UserCmdHandler

metadata = sqlalchemy.MetaData()
user_table = sqlalchemy.Table(
    "users", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(length=32)),
    sqlalchemy.Column("password", sqlalchemy.String(length=32)),
    sqlalchemy.Column("states", sqlalchemy.BLOB))


class GameServer(object, metaclass=Singleton):
    def __init__(self,
                 host,
                 port,
                 hz=20,
                 datapath="/home/samuel_vita/Documents/genix-dev/genix/data"):
        self.host = host
        self.port = port
        self.datapath = datapath

        self.active_users = {}

        self.loop = asyncio.get_event_loop()
        self.lock = Lock()
        self.refresh_rate = 1.0 / hz
        self.ticks = 0

        self.cmdq = Queue()
        self.cmd_handler = UserCmdHandler()

        self.world_map = WorldMap().load(f'{self.datapath}/world_map.pkl')

    @property
    def world_width(self):
        return self.world_map.width

    @property
    def world_height(self):
        return self.world_map.height

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

    @classmethod
    def get_instance(cls):
        return GameServer()

    @classmethod
    def popall(cls, q):
        ret = []
        while True:
            try:
                ret.append(q.get_nowait())
            except Empty:
                break
        return ret

    async def init_database(self):
        self.db = Database(f'sqlite:///{self.datapath}/genix.db')
        await self.db.connect()

    async def store_user(self, socket):
        if socket not in self.active_users:
            return
        player = self.active_users[socket]
        query = user_table.update().where(user_table.c.username == player.username)\
            .values(states=player.state.to_binary())
        await self.db.execute(query)
        del self.active_users[socket]
        socket.close()

    @async_guard_exception(False)
    @async_log_exception
    async def restore_user(self, socket, username, password):
        query = user_table.select().where((user_table.c.username == username) &
                                          (user_table.c.password == password))
        row = await self.db.fetch_one(query=query)
        if row:
            ps = PlayerState.from_binary(row["states"])
            self.active_users[socket] = Player(username, ps, self)
            logger.info("User login succesfully")
            return True

    @async_guard_exception(False)
    @async_log_exception
    async def register_user(self, socket, username, password):
        if len(password) < 2 or len(password) > 16:
            logger.error(f"Invalid password")
            return False

        query = user_table.insert()
        values = {
            "username": username,
            #  "password": hashlib.md5(password.encode("utf-8")).hexdigest(),
            "password": password,
            "states": b""
        }
        await self.db.execute(query=query, values=values)

        # inital user state
        ps = PlayerState.from_dict({
            "x": 95,
            "y": 90,
            "avatar": username[0].upper()
        })
        self.active_users[socket] = Player(username, ps, self)
        logger.info("User register succesfully")
        return True

    def validate_requests(self, tokens):
        if not isinstance(tokens, dict):
            return False
        demand_keys = ["username", "password", "action"]
        return all([k in tokens for k in demand_keys])

    @async_guard_exception(None)
    @async_log_exception
    async def user_connect(self, websocket, path):
        """
        Handle user connection, it return a msg which indicates either an success or error
            msg:
                -1: invalid login requests
                -2: invalid login user|password
                -3: invalid register password
                0: login success
                1: register success
        Args:
            websocket:
            path:

        Returns:
           msg (int):
        """
        logger.info("Server: try to Connect")

        # parse login requests
        tokens = pickle.loads(await websocket.recv())
        if not self.validate_requests(tokens):
            logger.error(f"Server: unvalid user connect request: {tokens}")
            return -1

        action, username, password = tokens["action"], tokens[
            "username"], tokens["password"]

        # deal with login or register
        if action == "login":
            flag = await self.restore_user(websocket, username, password)
            return 0 if flag else -2

        if action == "register":
            flag = await self.register_user(websocket, username, password)
            return 1 if flag else -3

    @async_guard_exception(None)
    async def client_step(self, websocket):
        player = self.active_users[websocket]
        await websocket.send(pickle.dumps(player.frames.get()))

        # recieve client updates
        #  cmds = await self.await_with_timeout(websocket.recv(), 0.05, None)
        cmds = await websocket.recv()
        if cmds is not None:
            cmds = pickle.loads(cmds)
            #  logger.info(f"Server: received cmds from client {cmds}")
            # add to the global cmds queue
            for c in cmds:
                self.cmdq.put_nowait((websocket, c))
        else:
            logger.info("timeout in receiving user cmds")

        #  player = self.active_users[websocket]
        #  await websocket.send(pickle.dumps(player.frames.get()))

    @guard_exception(None)
    @log_exception
    def lock_step(self):
        cmd_to_execute = deque(GameServer.popall(self.cmdq))
        logger.info(f"cmds to execute: {len(cmd_to_execute)}")
        self.cmd_handler.execute(self, cmd_to_execute)
        for _, p in self.active_users.items():
            self.update_client(p)

    def update_client(self, player):
        ap = player.state
        ops = [p.state for p in self.active_users.values() if p != player]
        #  logger.info(f"number of other players: {len(ops)}")
        world_map = self.world_map.get_slice(ap.x, ap.y, 400, 400)
        player.frames.put(NetFrame(ap, ops, world_map))

    async def serve_client(self, websocket, path):
        flag = -10
        while flag < 0:
            flag = await self.user_connect(websocket, path)
            if websocket.closed:
                logger.info("User abondon connect")
                return
            await websocket.send(pickle.dumps(flag))

        logger.info("User connection finished")

        while True:
            if websocket.closed:
                logger.info("User Deconnect")
                await self.store_user(websocket)
                return
            await self.client_step(websocket)

    def start_ticker(self):
        def _target():
            ts = time.time()
            #  beginning = ts
            #  tik = 0
            while True:
                self.lock_step()
                now = time.time()
                delta = self.refresh_rate - (now - ts)
                if delta > 0:
                    time.sleep(delta)

                with self.lock:
                    self.tick_ready = True
                    ts = time.time()

                    #  tik += 1
                    #  logger.info(f"tick rate: {tik/(ts - beginning)} FPS")

        self.ticker = Thread(target=_target)
        self.ticker.start()

    def run_co(self, func):
        self.loop.run_until_complete(func)

    async def await_with_timeout(self, coro, ts, default):
        try:
            async with timeout(ts):
                return await coro
        except asyncio.TimeoutError:
            return default

    def start(self):
        self.start_ticker()
        self.run_co(self.init_database())
        tcp_server = websockets.serve(self.serve_client, self.host, self.port)
        self.run_co(tcp_server)
        self.loop.run_forever()


if __name__ == '__main__':
    host, port = "127.0.0.1", 12345
    game_server = GameServer(host, port, hz=15)
    game_server.start()
