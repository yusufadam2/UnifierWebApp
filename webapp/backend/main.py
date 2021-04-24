import base64
import datetime
import os

import conversation
import crypto
import sqldb
import matching

from typing import Optional

from flask import abort, jsonify, request, Flask, session, redirect, url_for
from flask_session import Session
from datetime import datetime, date
#from flask_cors import CORS, cross_origin

CONVERSATION_ROOT = 'conversations'
conversation.ensure_fpath(CONVERSATION_ROOT)

DEFAULT_MATCH_COUNT = 5

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
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # limit requests to 2 MiB
sess = Session()


@app.route('/')
def main():
    return app.send_static_file('index.html')


# TODO(mikolaj): implement csrf protection
@app.route('/api/register', methods=['POST'])
def register():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    email = request.values.get('email')
    dob = request.values.get('dob')
    username = request.values.get('username')
    password = request.values.get('password')

    if email is None or dob is None or username is None or password is None:
        return app.response_class(status=400)

    query = 'SELECT * FROM UserAuth WHERE username LIKE ? OR email LIKE ?;'
    parameters = (username, email)
    existing_user = sqldb.do_sql(cur, query, parameters)

    if existing_user is not None and len(existing_user) > 0:
        return app.response_class(status=400)

    query = 'INSERT INTO Users (name, dob, pictureId) VALUES (?,?,?);'
    parameters = (username, dob, sqldb.DEFAULT_PICTURE_ID)
    sqldb.do_sql(cur, query, parameters)
    uid = cur.lastrowid

    query = 'INSERT INTO UserAuth (username, email, hash, salt, userId) VALUES (?,?,?,?,?);'
    parameters = (username, email, *crypto.hash_secret(password), uid)
    sqldb.do_sql(cur, query, parameters)

    conn.commit()

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

    print(matching_users)

    for uid, user_hash, user_salt in matching_users:
        if crypto.verify_secret(password, user_hash, user_salt):
            session['uid'] = uid
            return app.response_class(status=200)

    return app.response_class(status=401)


# TODO(mikolaj): implement csrf protection
@app.route('/api/logout', methods=['POST'])
def logout():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    session.pop('uid', None)
    session.pop('cid', None)

    return app.response_class(status=200, headers={'Clear-Site-Data': '"*", "cookies"'})


def load_user_profile(cur, uid) -> Optional:
    query = 'SELECT * FROM Users WHERE id LIKE ?;'
    parameters = (uid,)
    user_profile = sqldb.do_sql(cur, query, parameters)

    if user_profile is None or len(user_profile) == 0:
        return None

    uid, name, dob, gender, bio, picture_id = user_profile[0]

    query = 'SELECT data FROM UserPictures WHERE id LIKE ?;'
    parameters = (picture_id,)
    picture = sqldb.do_sql(cur, query, parameters)[0][0]
    picture_base64_bytes = base64.b64encode(picture)

    query = '''SELECT interestId FROM UsersInterestsJoin 
    INNER JOIN Users ON UsersInterestsJoin.userId = Users.id 
    INNER JOIN Interests ON UsersInterestsJoin.interestId = Interests.id 
    WHERE userId LIKE ?;'''
    parameters = (uid,)
    interests = sqldb.do_sql(cur, query, parameters)
    
    query = 'SELECT name FROM Interests WHERE id LIKE ?;'
    interest_names = [None] * len(interests)
    for idx, interest in enumerate(interests):
        interest_names[idx] = sqldb.do_sql(cur, query, interest)[0][0]

    return uid, name, dob, gender, bio, picture_base64_bytes, interest_names


@app.route('/api/readProfile', methods=['GET'])
def read_profile():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    # take the uid provided in the request, falling back to the session uid
    uid = request.values.get('uid', session.get('uid'))

    if (user_profile := load_user_profile(cur, uid)) is None:
        return app.response_class(status=400)

    uid, name, dob, gender, bio, picture_base64_bytes, interest_names = user_profile

    return jsonify({
        'uid': uid,
        'username': name,
        'dob': dob,
        'gender': gender,
        'biography': bio,
        'pictureBase64Src': picture_base64_bytes.decode('utf-8'),
        'interests': interest_names,
    })


@app.route('/api/updateProfile', methods=['POST'])
def update_profile():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = session.get('uid')

    print(request.values)
    print(request.files)

    name = request.values.get('name')
    dob = request.values.get('dob')
    interests = request.values.get('interests')
    biography = request.values.get('biography')
    gender = request.values.get('gender')

    picture = request.files.get('profilePictureUpload').read()

    if load_user_profile(cur, uid) is None:
        return app.response_class(status=400)

    query = 'UPDATE Users SET bio = ?, gender = ? WHERE id LIKE ?;'
    parameters = (biography, gender, uid)
    sqldb.do_sql(cur, query, parameters)
    
    if picture != b'':
        query = 'SELECT pictureId FROM Users WHERE id LIKE ?;'
        parameters = (uid,)
        picture_id = sqldb.do_sql(cur, query, parameters)[0][0]

        if picture_id == sqldb.DEFAULT_PICTURE_ID:
            query = 'INSERT INTO UserPictures (data) VALUES (?);'
            parameters = (picture,)
            sqldb.do_sql(cur, query, parameters)

            new_picture_id = cur.lastrowid

            query = 'UPDATE Users SET pictureId = ? WHERE id LIKE ?;'
            parameters = (new_picture_id, uid)
            sqldb.do_sql(cur, query, parameters)
        else:
            query = 'UPDATE UserPictures SET data = ? WHERE id LIKE ?;'
            parameters = (picture, picture_id)
            result = sqldb.do_sql(cur, query, parameters)

    if interests is not None and interests != '':
        interest_names = set(interests.split(','))
        interest_ids = set()

        query = 'SELECT id FROM Interests WHERE name LIKE ?;'
        for name in interest_names:
            i = sqldb.do_sql(cur, query, (name,))
            if i is not None and len(i) == 1:
                interest_ids.add(i[0][0])

        query = 'SELECT interestId FROM UsersInterestsJoin WHERE userId LIKE ?;'
        existing_interests = sqldb.do_sql(cur, query, (uid,))
        existing_interests = set([x[0] for x in existing_interests])

        added_interests = interest_ids.difference(existing_interests)
        removed_interests = existing_interests.difference(interest_ids)

        for interest_id in added_interests:
            query = 'INSERT INTO UsersInterestsJoin (userId, interestId) VALUES (?,?);'
            sqldb.do_sql(cur, query, (uid, interest_id))

        for interest_id in removed_interests:
            query = 'DELETE FROM UsersInterestsJoin WHERE userId LIKE ? AND interestId LIKE ?;'
            sqldb.do_sql(cur, query, (uid, interest_id))

    elif interests is not None and interests == '':
        query = 'DELETE FROM UsersInterestsJoin WHERE userId LIKE ?;'
        sqldb.do_sql(cur, query, (uid,))

    conn.commit()

    # return the newly updated user profile
    uid, name, dob, gender, bio, picture_base64_bytes, interest_names = load_user_profile(cur, uid) 

    return jsonify({
        'uid': uid,
        'username': name,
        'dob': dob,
        'gender': gender,
        'biography': bio,
        'pictureBase64Src': picture_base64_bytes.decode('utf-8'),
        'interests': interest_names,
    })


@app.route('/api/startConversation', methods=['POST'])
def start_conversation():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = session.get('uid')
    other_uid = request.values.get('other')

    query = '''SELECT a.conversationId FROM UsersConversationsJoin a
    INNER JOIN UsersConversationsJoin b ON a.conversationId = b.conversationId
    WHERE a.userId LIKE ? AND b.userId LIKE ?;'''
    parameters = (uid, other_uid)
    result = sqldb.do_sql(cur, query, parameters)

    if result is not None and len(result) > 0:
        session['cid'] = result[0][0]
        return app.response_class(status=200)

    query = 'INSERT INTO Conversations (fpath) VALUES (?);'
    parameters = ('',)
    sqldb.do_sql(cur, query, parameters)
    cid = cur.lastrowid

    new_fpath = f'{CONVERSATION_ROOT}/{cid}'

    query = 'UPDATE Conversations SET fpath = ? WHERE id = ?;'
    parameters = (new_fpath, cid)
    sqldb.do_sql(cur, query, parameters)

    query = '''INSERT INTO UsersConversationsJoin (userId, conversationId) 
    VALUES (?,?);'''
    sqldb.do_sql(cur, query, (uid, cid))
    sqldb.do_sql(cur, query, (other_uid, cid))

    conn.commit()

    session['cid'] = cid
    return app.response_class(status=200)


@app.route('/api/sendMessage', methods=['POST'])
def send_message():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = session.get('uid')
    cid = session.get('cid')
    message = request.values.get('content')
    date_time = datetime.utcnow()

    query = '''SELECT conversationId FROM UsersConversationsJoin 
    INNER JOIN Users ON UsersConversationsJoin.userId = Users.id 
    WHERE userId LIKE ? AND conversationId LIKE ?;'''

    parameters = (uid, cid)
    users_conversations = sqldb.do_sql(cur, query, parameters)

    if users_conversations is None or len(users_conversations) == 0:
        return app.response_class(status=400)

    query = '''SELECT fpath FROM Conversations 
    INNER JOIN UsersConversationsJoin ON UsersConversationsJoin.conversationId = Conversations.id 
    WHERE Conversations.id LIKE ?;'''

    parameters = (cid,)
    fpath = sqldb.do_sql(cur, query, parameters)

    if fpath is None or len(fpath) == 0:
        return app.response_class(status=200)

    conversation.write_message(fpath[0][0], date_time, uid, message)
    return app.response_class(status=200)


@app.route('/api/fetchMessages', methods=['GET'])
def fetch_messages():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = session.get('uid')
    cid = session.get('cid')
    from_date = request.values.get('fromDate')
    from_time = request.values.get('fromTime')

    query = '''SELECT fpath FROM UsersConversationsJoin 
    INNER JOIN Conversations ON UsersConversationsJoin.conversationId = Conversations.id
    WHERE userId LIKE ? AND conversationId LIKE ?;'''
    parameters = (uid, cid)
    fpath = sqldb.do_sql(cur, query, parameters)

    if fpath is None or len(fpath) == 0:
        return app.response_class(status=400)

    try:
        from_date_index = int(from_date)
    except Exception:
        from_date_index = -1

    try:
        from_time_index = int(from_time)
    except Exception:
        from_time_index = -1
    
    msgs_to_read = conversation.read_messages(fpath[0][0], from_date_index, from_time_index)

    return jsonify([{'timestamp': t[0], 'datestamp': t[1], 'content': t[3], 'isLocal': int(t[2]) == uid} for t in msgs_to_read])


@app.route('/api/interests', methods = ['GET'])
def fetch_all_interests():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    query = '''SELECT InterestCategories.name, Interests.name FROM InterestCategories
    INNER JOIN Interests ON Interests.categoryId = InterestCategories.id
    ORDER BY InterestCategories.name;'''
    results = sqldb.do_sql(cur, query)

    interests = dict()
    for category, interest in results:
        prev = interests.get(category, [])
        prev.append(interest)
        interests[category] = prev

    return jsonify(interests)


@app.route('/api/friends', methods = ['GET'])
def fetch_all_friends():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()   

    uid = session.get('uid')

    query = '''SELECT conversationId FROM UsersConversationsJoin
    WHERE userId LIKE ?;'''
    parameters = (uid,)
    conversations = sqldb.do_sql(cur, query, parameters)

    if conversations is None:
        return []

    friend_ids = []

    query = '''SELECT userId FROM UsersConversationsJoin
    WHERE userId <> ? AND conversationId LIKE ?;'''

    for idx, tup in enumerate(conversations):
        parameters = (uid, tup[0])
        friends = sqldb.do_sql(cur, query, parameters)

        if friends is None or len(friends) == 0:
            continue

        for friend_id in friends:
            friend_ids.append(friend_id)

    return jsonify(friend_ids)


@app.route('/api/fetchMatches', methods = ['GET'])
def fetch_best_matches():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor() 

    uid = session.get('uid')
    match_count = int(request.values.get('matches', DEFAULT_MATCH_COUNT))

    query = '''SELECT interestId FROM UsersInterestsJoin WHERE userId LIKE ?;'''
    parameters = (uid,)
    interest_ids = [tup[0] for tup in sqldb.do_sql(cur, query, parameters)]

    matches = matching.n_best_matches(cur, uid, interest_ids, match_count)

    return jsonify([{'uid': match[0], 'score': match[1]} for match in matches])

