#!/usr/bin/env python
# -*- coding: utf-8 -*-

from databases import Database
import sqlalchemy
import asyncio
import sqlite3
import os

query = """
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, states BLOB)
"""
datapath = "/home/samuel_vita/Documents/genix-dev/genix/data"

metadata = sqlalchemy.MetaData()
user_table = sqlalchemy.Table(
    "users", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(length=32)),
    sqlalchemy.Column("password", sqlalchemy.String(length=32)),
    sqlalchemy.Column("states", sqlalchemy.BLOB))


async def init():
    os.remove(f"{datapath}/genix.db")

    db = Database(f"sqlite:///{datapath}/genix.db")

    await db.connect()
    await db.execute(query=query)

    q = user_table.insert()
    vals = [{"username": "test", "password": "test", "states": b"nothing"}]
    await db.execute_many(query=q, values=vals)

    q = user_table.select()
    rows = await db.fetch_all(q)
    for row in rows:
        print(row["username"], row["states"].decode("utf-8"))

    await db.disconnect()


def init_db():
    asyncio.get_event_loop().run_until_complete(init())


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)

    return conn


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def show_db():
    database = f"{datapath}/genix.db"
    # create a database connection
    conn = create_connection(database)
    with conn:
        select_all_tasks(conn)


if __name__ == '__main__':
    #  init_db()
    show_db()
