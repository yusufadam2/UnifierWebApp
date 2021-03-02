import crypto
import sqldb

from flask import json, request, Flask, session, redirect, url_for


# TODO(mikolaj): remove static_* parameters for production
app = Flask(__name__, static_url_path='', static_folder='../static')

app.secret_key = 'W6-COMP10120'
app.token_key = 'csrf_token'


@app.route('/')
def main():
    return app.send_static_file('index.html')


@app.route('/test/')
def test():
    data = ['foo', 'bar', 42]
    return app.response_class(response=json.dumps(data), status=200, mimetype='application/json')


# TODO(mikolaj): implement csrf protection
# TODO(daim): implement registration REST end point
@app.route('/register', methods=['POST'])
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
@app.route('/login', methods=['POST'])
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
            session['userId'] = uid
            redirect('/')

            return app.response_class(status=200)

    return app.response_class(status=400)


# TODO(mikolaj): implement csrf protection
@app.route('/logout', methods=['POST'])
def logout():
    conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()

    uid = request.values.get('uid', None)

    if uid is None:
        return app.response_class(status=400)

    session.pop('uid')

    print(f'[user-{uid}] Logged out!')
    redirect('/')

    return app.response_class(status=200)

