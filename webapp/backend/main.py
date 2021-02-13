from flask import json, request, Flask


# TODO(mikolaj): remove static_* parameters for production
app = Flask(__name__, static_url_path='', static_folder='../static')

app.secret_key = 'W6-CCOMP10120'
app.token_key = 'csrf_token'


@app.route('/')
def main():
    return app.send_static_file('index.html')


@app.route('/test/')
def test():
    data = ['foo', 'bar', 42]
    return app.response_class(
            response=json.dumps(data), status=200, mimetype='application/json')


@app.route('/register/', methods=['POST'])
def register():
    email = request.args['email']
    username = request.args['user']
    password = request.args['pass']

    return app.response_class(status=200)


@app.route('/login/', methods=['POST'])
def login():
    username = request.args['user']
    password = request.args['pass']

    print(f'User: {username}, Pass: {password}')

    return app.response_class(status=200)


@app.route('/userauth/')
def userauth():
    data = ['foo', 'bar']
    return app.response_class(
            response=json.dumps(data), status=200, mimetype='application/json')


@app.route('/users/')
def users():
    data = ['foo', 'bar']
    return app.response_class(
            response=json.dumps(data), status=200, mimetype='application/json')

