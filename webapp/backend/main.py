import os

import crypto
import sqldb

from flask import json, request, Flask, session, redirect, url_for
from flask_session import Session


# TODO(mikolaj): remove static_* parameters for production
app = Flask(__name__, static_url_path='', static_folder='../static')

SESSION_COOKIE_NAME = 'unifier-session'
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = True

SESSION_TYPE = 'filesystem'
SECRET_KEY = os.urandom(16)

app.config.from_object(__name__)
sess = Session()


@app.route('/')
def main():
    return app.send_static_file('index.html')


# TODO(mikolaj): implement csrf protection
# TODO(daim): implement registration REST end point
@app.route('/api/register', methods=['POST'])
def register():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    email = request.values.get('email', None)
    username = request.values.get('username', None)
    password = request.values.get('password', None)

    if email is None or username is None or password is None:
        return app.response_class(status=400)

    query = 'SELECT * FROM UserAuth WHERE username LIKE ? OR email LIKE ?'
    parameters = (username, email)
    existing_user = sqldb.do_sql(cur, query, parameters)

    if existing_user is not None:
        print(f'Username/email already exists!')
        return app.response_class(status=400)

    print(f'Registering user: {username} ({email}) with password {password}')

    query = 'INSERT INTO UserAuth (username, email, hash, salt) VALUES (?,?,?,?,?);'
    sqldb.do_sql(cur, CREATE_USER_AUTH_QUERY, (username, email, *crypto.hash_secret(password)))

    print(f'Succesfuly registered user: {username} ({email})')

    return app.response_class(status=200)


# TODO(mikolaj): implement csrf protection
@app.route('/api/login', methods=['POST'])
def login():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    username = request.values.get('username', None)
    password = request.values.get('password', None)

    if username is None or password is None:
        return app.response_class(status=400)

    query = 'SELECT userId, hash, salt FROM UserAuth WHERE username LIKE ?'
    parameters = (username,)
    matching_users = sqldb.do_sql(cur, query, parameters)

    for uid, user_hash, user_salt in matching_users:
        if crypto.verify_secret(password, user_hash, user_salt):
            print(f'[user-{uid}] Logged in!')
            session['uid'] = uid
            redirect('/')

            return app.response_class(status=200)

    return app.response_class(status=400)


# TODO(mikolaj): implement csrf protection
@app.route('/api/logout', methods=['POST'])
def logout():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = session.get('uid', None)

    if uid is None:
        return app.response_class(status=400)

    session.pop('uid')

    print(f'[user-{uid}] Logged out!')
    redirect('/')

    return app.response_class(status=200)

