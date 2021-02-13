"""
This module provides a helper function for executing sql queries.
"""

__all__ = ['DB', 'NAME_LEN', 'DESC_LEN', 'HASH_LEN', 'PATH_LEN', 'do_sql']

import enum
import sqlite3 as sql

from typing import List, Optional, Tuple

## TODO:
## - Read from db tables (SELECT ...)
## - Create new db table entries (INSERT ...)
## - Update db table entries (UPDATE ...)
## - Relational queries across db tables


DB = 'w6-comp10120.db'
NAME_LEN = 100
DESC_LEN = 4096
HASH_LEN = 512
PATH_LEN = 256


def do_sql(cur: sql.Cursor, query: str, parameters: Tuple = None) -> Optional:
    """
    Executes the given sql query (with the given parameters; use ? in 
    place of the actual parameter value) using the given cursor object.
    """
    try:
        if parameters is not None:
            cur.execute(query, parameters)
        else:
            cur.execute(query)

        return cur.fetchall()

    except sql.OperationalError as err:
        return None


def bootstrap():
    conn = sql.connect(DB)
    cur = conn.cursor()

    do_sql(cur, '''DROP TABLE UserAuth''')
    do_sql(cur, '''CREATE TABLE UserAuth(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        hash VARCHAR(512) UNIQUE NOT NULL,
        salt VARCHAR(512) UNIQUE NOT NULL,
        iter INTEGER NOT NULL,
        userId INTEGER UNIQUE NOT NULL,
        FOREIGN KEY(userId) REFERENCES Users(id));''')

    do_sql(cur, '''DROP TABLE Users''')
    do_sql(cur, '''CREATE TABLE Users(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        dob DATE NOT NULL,
        gender VARCHAR(100) NOT NULL,
        bio VARCHAR(4096),
        pictureId INTEGER NOT NULL,
        FOREIGN KEY(pictureId) REFERENCES UserPictures(id));''')

    do_sql(cur, '''DROP TABLE UserPictures''')
    do_sql(cur, '''CREATE TABLE UserPictures(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        data BLOB NOT NULL);''')

    do_sql(cur, '''DROP TABLE Interests''')
    do_sql(cur, '''CREATE TABLE Interests(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL);''')

    do_sql(cur, '''DROP TABLE UsersInterestsJoins''')
    do_sql(cur, '''CREATE TABLE UsersInterestsJoins(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        userId INTEGER NOT NULL,
        interestId INTEGER NOT NULL,
        FOREIGN KEY(userId) REFERENCES Users(id),
        FOREIGN KEY(interestId) REFERENCES Interests(id));''')

    do_sql(cur, '''DROP TABLE Conversations''')
    do_sql(cur, '''CREATE TABLE Conversations(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        fpath VARCHAR(256) UNIQUE NOT NULL);''')

    do_sql(cur, '''DROP TABLE UsersConversationsJoin''')
    do_sql(cur, '''CREATE TABLE UsersConversationsJoin(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        userId INTEGER NOT NULL,
        conversationId INTEGER NOT NULL,
        FOREIGN KEY(userId) REFERENCES Users(id),
        FOREIGN KEY(conversationId) REFERENCES Conversations(id));''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    print('Hello World!')
    bootstrap()

