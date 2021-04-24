"""
This module provides a helper function for executing sql queries.
"""

__all__ = [
        'DB', 'DEFAULT_PICTURE_ID', 'NAME_LEN', 'DESC_LEN', 'HASH_LEN', 
        'SALT_LEN', 'PATH_LEN',
        'close_conn', 'do_sql', 'try_open_conn'
]

import enum
import sqlite3 as sql

import crypto

from datetime import datetime
from typing import List, Optional, Tuple

from pprint import pprint

## TODO:
## - Read from db tables (SELECT ...)
## - Create new db table entries (INSERT ...)
## - Update db table entries (UPDATE ...)
## - Relational queries across db tables


DB = 'w6-comp10120.db'
NAME_LEN = 100
DESC_LEN = 4096
HASH_LEN = crypto.CRYPTO_HASH_LEN
SALT_LEN = crypto.CRYPTO_SALT_LEN
PATH_LEN = 256

DEFAULT_PICTURE_ID = 1

def close_conn(conn: sql.Connection):
    """
    Closes the given database connection.
    """
    conn.commit()
    conn.close()


def try_open_conn() -> Optional[sql.Connection]:
    """
    Attempts to open a connection to the database.
    """
    try:
        conn = sql.connect(DB)
        return conn

    except sql.OperationalError as err:
        return None


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
        print(f'Error executing {query} with parameters {parameters}: {err}')
        return None


def bootstrap():
    conn = sql.connect(DB)
    cur = conn.cursor()

    # create tables
    do_sql(cur, '''DROP TABLE UserAuth;''')
    do_sql(cur, '''CREATE TABLE UserAuth(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        hash VARCHAR(512) UNIQUE NOT NULL,
        salt VARCHAR(512) UNIQUE NOT NULL,
        userId INTEGER UNIQUE NOT NULL,
        FOREIGN KEY(userId) REFERENCES Users(id));''')

    do_sql(cur, '''DROP TABLE Users;''')
    do_sql(cur, '''CREATE TABLE Users(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        dob DATE NOT NULL,
        gender VARCHAR(100),
        bio VARCHAR(4096),
        pictureId INTEGER NOT NULL,
        FOREIGN KEY(pictureId) REFERENCES UserPictures(id));''')

    do_sql(cur, '''DROP TABLE UserPictures;''')
    do_sql(cur, '''CREATE TABLE UserPictures(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        data BLOB NOT NULL);''')

    do_sql(cur, '''DROP TABLE InterestCategories;''')
    do_sql(cur, '''CREATE TABLE InterestCategories(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL);''')

    do_sql(cur, '''DROP TABLE Interests;''')
    do_sql(cur, '''CREATE TABLE Interests(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        categoryId INTEGER NOT NULL,
        FOREIGN KEY(categoryId) REFERENCES InterestCategories(id));''')

    do_sql(cur, '''DROP TABLE UsersInterestsJoin;''')
    do_sql(cur, '''CREATE TABLE UsersInterestsJoin(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        userId INTEGER NOT NULL,
        interestId INTEGER NOT NULL,
        FOREIGN KEY(userId) REFERENCES Users(id),
        FOREIGN KEY(interestId) REFERENCES Interests(id));''')

    do_sql(cur, '''DROP TABLE Conversations;''')
    do_sql(cur, '''CREATE TABLE Conversations(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        fpath VARCHAR(256) UNIQUE NOT NULL);''')

    do_sql(cur, '''DROP TABLE UsersConversationsJoin;''')
    do_sql(cur, '''CREATE TABLE UsersConversationsJoin(
        id INTEGER UNIQUE NOT NULL PRIMARY KEY,
        userId INTEGER NOT NULL,
        conversationId INTEGER NOT NULL,
        FOREIGN KEY(userId) REFERENCES Users(id),
        FOREIGN KEY(conversationId) REFERENCES Conversations(id));''')

    # insert data
    default_picture_fpath = 'default_profile_picture.png'
    with open(default_picture_fpath, 'rb') as default_picture_file:
        default_picture_blob = default_picture_file.read()

        CREATE_USER_PICTURE_QUERY = 'INSERT INTO UserPictures (id, data) VALUES (?,?);'
        do_sql(cur, CREATE_USER_PICTURE_QUERY, (DEFAULT_PICTURE_ID, default_picture_blob))

    CREATE_USER_QUERY = 'INSERT INTO Users (name, dob, pictureId) VALUES (?,?,?);'
    do_sql(cur, CREATE_USER_QUERY, ('John Doe', datetime.now(), 1))
    do_sql(cur, CREATE_USER_QUERY, ('Jane Doe', datetime.now(), 1))
    do_sql(cur, CREATE_USER_QUERY, ('Foo Bar', datetime.now(), 1))
    do_sql(cur, CREATE_USER_QUERY, ('Chad Thunder', datetime.now(), 1))

    CREATE_USER_AUTH_QUERY = 'INSERT INTO UserAuth (username, email, hash, salt, userId) VALUES (?,?,?,?,?);'
    do_sql(cur, CREATE_USER_AUTH_QUERY, ('jdoe1991', 'john.doe@gmail.com', *crypto.hash_secret('password'), 1))
    do_sql(cur, CREATE_USER_AUTH_QUERY, ('jane_doe', 'jane.doe@gmail.com', *crypto.hash_secret('ABetterPassword!'), 2))
    do_sql(cur, CREATE_USER_AUTH_QUERY, ('foobar', 'foobar@gmail.com', *crypto.hash_secret('foobar?'), 3))
    do_sql(cur, CREATE_USER_AUTH_QUERY, ('cthunder', 'chad@thunder.net', *crypto.hash_secret('GreasedLightning123'), 4))

    CREATE_CATEGORY_QUERY = 'INSERT INTO InterestCategories (name) VALUES (?);'
    CREATE_INTEREST_QUERY = 'INSERT INTO Interests (name, categoryId) VALUES (?, ?);'
    category_to_interest_map = {
        'sport': ['football', 'basketball', 'karate', 'badminton', 'pingpong', 'mma', 'skiing', 'weightlifting', 'snowboarding', 'marathons', 'hockey', 'cricket', 'rugby'],
        'outdoor': ['hiking', 'camping', 'stargazing'],
        'creative': ['woodworking', 'painting', 'writing'],
        'classical': ['reading', 'music', 'languages'],
        'games': ['chess', 'crosswords', 'puzzles'],
    }

    interest_to_category_map = dict()
    for category, interests in category_to_interest_map.items():
        do_sql(cur, CREATE_CATEGORY_QUERY, (category,))
        for interest in interests:
            interest_to_category_map[interest] = category

    interests = sorted(interest_to_category_map)

    FETCH_CATEGORY_ID_QUERY = 'SELECT id FROM InterestCategories WHERE name LIKE ?;'
    for i in interests:
        category_ids = do_sql(cur, FETCH_CATEGORY_ID_QUERY, (interest_to_category_map[i],))
        do_sql(cur, CREATE_INTEREST_QUERY, (i, category_ids[0][0]))

    FETCH_INTEREST_ID_QUERY = 'SELECT id FROM Interests WHERE name LIKE ?;'
    def get_interest_id(interest_name):
        return do_sql(cur, FETCH_INTEREST_ID_QUERY, (interest_name,))[0][0]

    JOIN_USER_INTEREST_QUERY = 'INSERT INTO UsersInterestsJoin (userId, interestId) VALUES (?,?);'
    johns_interests = ['badminton', 'hiking', 'crosswords']
    for i in johns_interests:
        do_sql(cur, JOIN_USER_INTEREST_QUERY, (1, get_interest_id(i)))

    janes_interests = ['woodworking', 'painting', 'languages']
    for i in janes_interests:
        do_sql(cur, JOIN_USER_INTEREST_QUERY, (2, get_interest_id(i)))

    foobars_interests = [i for i in interests]
    for i in foobars_interests:
        do_sql(cur, JOIN_USER_INTEREST_QUERY, (3, get_interest_id(i)))

    chads_interests = ['football', 'basketball', 'mma', 'weightlifting', 'hockey', 'rugby']
    for i in chads_interests:
        do_sql(cur, JOIN_USER_INTEREST_QUERY, (4, get_interest_id(i)))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    print('Hello World!')
    bootstrap()

