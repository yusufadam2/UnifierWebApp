import os

import conversation
import crypto
import sqldb
import matching

import datetime

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
sess = Session()


@app.route('/')
#@cross_origin()
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

    query = 'SELECT * FROM UserAuth WHERE username LIKE ? OR email LIKE ?;'
    parameters = (username, email)
    existing_user = sqldb.do_sql(cur, query, parameters)

    if existing_user is not None:
        print(f'Username/email already exists!')
        return app.response_class(status=400)

    print(f'Registering user: {username} ({email}) with password {password}')

    query = 'INSERT INTO UserAuth (username, email, hash, salt) VALUES (?,?,?,?,?);'
    parameters = (username, email, *crypto.hash_secret(password))
    sqldb.do_sql(cur, query, parameters)

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


@app.route('/api/readProfile', methods=['GET'])
def read_profile():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    # take the uid provided in the request, falling back to the session uid
    uid = request.values.get('uid', session.get('uid'))

    query = '''SELECT * FROM Users
    WHERE id LIKE ?;'''
    parameters = (uid,)
    user_profile = sqldb.do_sql(cur, query, parameters)[0]
    uid, name, dob, gender, bio, picture_id = user_profile

    query = '''SELECT data FROM UserPictures
    WHERE id LIKE ?;'''
    parameters = (picture_id,)
    picture = sqldb.do_sql(cur, query, parameters)[0][0]

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

    return jsonify({
        'uid': uid,
        'username': name,
        'dob': dob,
        'gender': gender,
        'biography': bio,
        'picture': 1,
        'interests': interest_names,
    })


#update interests left to do
@app.route('/api/updateProfile', methods=['POST'])
def update_profile():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = session.get('uid')
    name = request.values.get('name')
    dob = request.values.get('dob')
    interests = request.values.get('interests')
    biography = request.values.get('biography')
    gender = request.values.get('gender')
    profilePicture = request.values.get('profilePicture')

    print(request.values)

    interests_list = interests.split(',')

    query = '''SELECT * FROM Users
    WHERE id LIKE ?;'''
    parameters = (uid,)

    user_exist = sqldb.do_sql(cur, query, parameters)

    if user_exist is None:
#        query = '''INSERT INTO UserPictures(data) VALUES (?);'''
#        parameters = ('',)
#        sqldb.do_sql(cur, query, parameters)
#        picture_id = cur.lastrowindex

        query = '''INSERT INTO Users (id, name, dob, gender, bio, pictureId) 
        VALUES (?,?,?,?,?,?);'''
        parameters = (uid, name, dob, gender, biography, 1)
        sqldb.do_sql(cur, query, parameters)

        for interest in interests_list:
            interest_id = sqldb.get_interest_id(interest)
            query_interest = 'INSERT INTO UsersInterestsJoin (userId, interestId) VALUES (?,?);'
            do_sql(cur, query_interest, (uid, interest_id))

    else: 
        query = '''UPDATE Users SET bio = ?, gender = ? WHERE id LIKE ?;'''
        parameters = (biography, gender, uid)
        sqldb.do_sql(cur, query, parameters)

#        query = '''SELECT pictureId FROM Users WHERE id LIKE ?;'''
#        parameters = (uid,)
#        picture_id = sqldb.do_sql(cur, query, parameters)

#        query = '''UPDATE UserPictures
#        SET data = ?
#        WHERE id LIKE ?;'''
#        parameters = (profilePicture, picture_id)
#        cur.execute(query, parameters)

#        for interest in interests_list:
#            interest_id = sqldb.get_interest_id(interest)
#            existing_interests = do_sql(cur, 'SELECT interestId FROM UsersInterestsJoin WHERE userId LIKE ?;', (uid,))
#            if (interest in existing_interests):
#                continue;
#            else:
#                query_interest = 'INSERT INTO UsersInterestsJoin (userId, interestId) VALUES (?,?);'
#                do_sql(cur, query_interest, (uid, interest_id))

    return app.response_class(status=200)


@app.route('/api/startConversation', methods=['POST'])
def start_conversation():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = session.get('uid')
    other_uid = request.values.get('other')

    query = '''SELECT userId, conversationId FROM UsersConversationsJoin
    WHERE userId LIKE ?;'''
    parameters = (other_uid,)
    result = sqldb.do_sql(cur, query, parameters)

    if result is None or len(result) == 0:
        query = '''INSERT INTO Conversations (fpath) 
        VALUES (?);'''
        parameters = ('',)
        sqldb.do_sql(cur, query, parameters)
        cid = cur.lastrowid

        new_fpath = f'{CONVERSATION_ROOT}/{cid}'

        query = '''UPDATE Conversations
        SET fpath = ?
        WHERE id = ?;'''
        parameters = (new_fpath, cid)
        sqldb.do_sql(cur, query, parameters)

        query = '''INSERT INTO UsersConversationsJoin (userId, conversationId) 
        VALUES (?,?);'''
        sqldb.do_sql(cur, query, (uid, cid))
        sqldb.do_sql(cur, query, (other_uid, cid))

        conn.commit()

        session['cid'] = cid
        
        return app.response_class(status=200)

    session['cid'] = result[0][1]
    print(session['cid'])

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
    INNER JOIN Users ON UsersConversationsJoin.userId = Users.id 
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

    query = '''SELECT name FROM Interests;'''
    all_interests = sqldb.do_sql(cur, query)

    return jsonify([tup[0] for tup in all_interests])


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

