#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  import hashlib

import sqlalchemy
from databases import Database
from loguru import logger

from genix.common.entity import PlayerState
from genix.common.util import async_guard_exception, async_log_exception
from genix.server.entity import Player

metadata = sqlalchemy.MetaData()
user_table = sqlalchemy.Table(
    "users", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(length=32)),
    sqlalchemy.Column("password", sqlalchemy.String(length=32)),
    sqlalchemy.Column("states", sqlalchemy.BLOB))


class GenixDB:
    def __init__(self, uri, debug=False):
        self.uri = uri
        self.engine = Database(uri)
        self.debug = debug

    async def connect(self):
        await self.engine.connect()
        if self.debug:
            logger.info(f"Connection to db {self.uri}")

    @async_guard_exception(False)
    @async_log_exception
    async def update_user(self, player):
        query = user_table.update()\
                    .where(user_table.c.username == player.username)\
                    .values(states=player.state.to_binary())
        await self.engine.execute(query)
        if self.debug:
            logger.info(f"Updated user {player.username} to db")
        return True

    @async_guard_exception(None)
    @async_log_exception
    async def restore_user(self, username, password):
        query = user_table.select().where((user_table.c.username == username) &
                                          (user_table.c.password == password))
        row = await self.engine.fetch_one(query=query)
        if row:
            ps = PlayerState.from_binary(row["states"])
            if self.debug:
                logger.info(f"Restored {username} from db")
            return Player(username, ps)

    @async_guard_exception(None)
    @async_log_exception
    async def register_user(self, username, password, x0, y0):
        if len(password) < 2 or len(password) > 16:
            logger.error(f"Register: invalid password")
            return None

        query = user_table.insert()
        values = {
            "username": username,
            #  "password": hashlib.md5(password.encode("utf-8")).hexdigest(),
            "password": password,
            "states": b""
        }
        await self.engine.execute(query=query, values=values)

        # inital user state
        ps = PlayerState.from_dict({
            "x": x0,
            "y": y0,
            "avatar": username[0].upper()
        })
        if self.debug:
            logger.info("User register succesfully")
        return Player(username, ps)
