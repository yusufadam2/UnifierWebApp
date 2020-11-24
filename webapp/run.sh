#!/bin/sh

. env/bin/activate

export FLASK_APP='main.py'
export FLASK_ENV='production'
flask run

deactivate
