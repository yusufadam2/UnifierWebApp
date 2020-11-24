from flask import Flask


app = Flask(
        __name__,
        static_url_path='',
        static_folder='../static') # TODO: Remove static url for deploy
app.secret_key = 'W6-CCOMP10120'
app.token_key = 'csrf_token'


@app.route('/')
def main():
    return app.send_static_file('index.html')

