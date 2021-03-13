import os

import crypto
import sqldb

from flask import json, request, Flask, session, redirect, url_for
from flask_session import Session
from datetime import datetime


# TODO(mikolaj): remove static_* parameters for production
app = Flask(__name__, static_url_path='', static_folder='../static')

SESSION_COOKIE_NAME = 'unifier-session'
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = True

SESSION_TYPE = 'filesystem'

SECRET_KEY = b'\x11\xe7\x18\xbd\xf1\xban&a\x9ap\xa5\xdbc\xb2\xfa'

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
    sqldb.do_sql(cur, query, (username, email, *crypto.hash_secret(password)))

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

    query = 'SELECT userId, hash, salt FROM UserAuth WHERE username LIKE ?;'
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


@app.route('/api/readProfile', methods=['GET'])
def readProfile:
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = request.args.get('uid')

    query = 'SELECT * FROM Users WHERE id LIKE ?;'
    parameters = (uid,)
    cur.execute(query, parameters)
    profile = cur.fetchone()

    query2 = 'SELECT data FROM UserPictures WHERE id LIKE ?;'
    picId = profile[5]
    parameters2 = (picId,)
    cur.execute(query2, parameters2)
    profilePic = cur.fetchone()

    query3 = 'SELECT interestId FROM UsersInterestsJoin INNER JOIN Users ON UsersInterestsJoin.userId = Users.id INNER JOIN Interests ON UsersInterestsJoin.interestId = Interests.id WHERE userId LIKE ?;'
    parameters3 = (uid,)
    profileInterestsId = sqldb.do_sql(cur, query3, parameters3)

    query4 = 'SELECT name FROM Interests WHERE id LIKE ?;'
    profileInterests = sqldb.do_sql(cur, query4, profileInterestsId)

    finalProfile =  (profile + profilePic + profileInterests)

    return finalProfile


#update interests left to do
@app.route('/api/updateProfile', methods=['GET'])
def updateProfile:
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = request.args.get('uid')
    name = request.args.get('name')
    dob = user.args.get('dob')
    interests = request.args.get('interests')
    biography = request.args.get('biography')
    gender = request.args.get('gender')
    profilePicture = request.args.get('profilePicture')

    interests_list = interests.split(",")

    user_exist = sqldb.do_sql(cur, 'SELECT * FROM Users WHERE id LIKE ?;', uid)

    if user_exist is None:
        query = 'INSERT INTO Users (id, name, dob, gender, bio) VALUES (?,?,?,?,?);'
        parameters = (uid, name, dob, gender, biography)
        cur.execute(query, parameters)

        query = 'INSERT INTO UserPictures(data) VALUES (?);'
        parameters = (profilePicture,)
        cur.execute(query, parameters)

        for interest in interests_list:
            interest_id = sqldb.get_interest_id(interest)
            query_interest = 'INSERT INTO UsersInterestsJoin (userId, interestId) VALUES (?,?);'
            do_sql(cur, query_interest, (uid, interest_id))

    else: 
        query = 'UPDATE Users SET bio = ?, gender = ? WHERE id LIKE ?;'
        parameters = (biography, gender, uid)
        cur.execute(query, parameters)

        query = 'SELECT pictureId FROM Users WHERE id LIKE ?;'
        parameters = (uid,)
        cur.execute(query, parameters)
        picId = cur.fetchone()

        query = 'UPDATE UserPictures SET data = ? INNER JOIN Users ON UserPictures.id = Users.pictureId WHERE id LIKE ?;'
        parameters = (profilePicture, picId)
        cur.execute(query, parameters)

        for interest in interest_list:
            interest_id = sqldb.get_interest_id(interest)
            existing_interests = do_sql(cur, 'SELECT interestId FROM UsersInterestsJoin WHERE userId LIKE ?;', (uid,))
            if (interest in existing_interests):
                continue;
            else:
                query_interest = 'INSERT INTO UsersInterestsJoin (userId, interestId) VALUES (?,?);'
                do_sql(cur, query_interest, (uid, interest_id))

    return app.response_class(status=200)


@app.route('/api/sendMessage', methods=['POST'])
def sendMessage:
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = request.args.get('uid')
    cid = request.args.get('cid')
    message = request.args.get('message')
    date_time = datetime.utcnow()

    query = 'SELECT converstaionId FROM UsersConversatinsJoin INNER JOIN Users ON UsersConversatinsJoin.userId = Users.id WHERE userId LIKE ? AND converstaionId LIKE ?;'
    parameters = (uid, cid)
    convoValidation = sqldb.do_sql(cur, query, parameters)

    if convoValidation is None:
        print(f'User does not have access to this conversation!')
        return app.response_class(status=400)

    query2 = 'SELECT fpath FROM Conversations INNER JOIN UsersConversatinsJoin ON UsersConversatinsJoin.converstaionId = Conversations.id WHERE id LIKE ?;'
    parameters2 = (cid,)
    cur.execute(query2, parameters2)
    fpath = cur.fetchone()

    write_message(fpath, date_time, uid, message)
    return app.response_class(status=200)


@app.route('/api/fetchMessages', methods=['GET'])
def fetchMessages:
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = request.args.get('uid')
    cid = request.args.get('cid')
    message = request.args.get('message')
    fromDate = request.args.get('fromDate')

    query = 'SELECT converstaionId FROM UsersConversatinsJoin INNER JOIN Users ON UsersConversatinsJoin.userId = Users.id WHERE userId LIKE ? AND converstaionId LIKE ?;'
    parameters = (uid, cid)
    convoValidation = sqldb.do_sql(cur, query, parameters)

    if convoValidation is None:
        print(f'User does not have access to this conversation!')
        return app.response_class(status=400)

    query2 = 'SELECT fpath FROM Conversations INNER JOIN UsersConversatinsJoin ON UsersConversatinsJoin.converstaionId = Conversations.id WHERE id LIKE ?;'
    parameters2 = (cid,)
    cur.execute(query2, parameters2)
    fpath = cur.fetchone()

    msgs_to_read = read_messages(fpath, fromDate)


    return msgs_to_read






