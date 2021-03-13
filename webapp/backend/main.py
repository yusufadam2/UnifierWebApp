import crypto
import sqldb
import daytime

from flask import json, request, Flask


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
    parameters = (username)
    matching_users = sqldb.do_sql(cur, query, parameters)

    for uid, user_hash, user_salt in matching_users:
        if crypto.verify_secret(password, user_hash, user_salt):
            print(f'[user-{uid}] Logged in!')

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

    print(f'[user-{uid}] Logged out!')

    return app.response_class(status=200)

def read_message(fpath,fromDate):
    date_list = []  
    begin_date = datetime.datetime.strptime(fromDate, "%d-%m-%Y")  
    end_date = datetime.datetime.strptime(time.strftime('%d-%m-%Y',time.localtime(time.time())), "%d-%m-%Y")

    while begin_date <= end_date:  
        date_str = begin_date.strftime("%d-%m-%Y")  
        date_list.append(fpath+date_str+".conv") 
        begin_date += datetime.timedelta(days=1)

    for item in date_list:
        with open(item,'r') as message:
            contents = message.readlines()

    return contents


def write_message(uid,fpath,message,date):
    date_file = str(date)+".conv"

    if not (os.path.isdir(fpath)):
        return app.response_class(status=400)

    date_path = fpath+date_file
    os.mknod(date_path)

    message = (uid,message)
    with open(date_file,"w") as conversation:
        conversation.write(message)
