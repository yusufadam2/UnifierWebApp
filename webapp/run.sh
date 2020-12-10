#!/bin/sh

## !!!! THIS IS THE STARTUP SCRIPT FOR THE PRODUCTION SERVER !!!!
## !!!! DURING DEVELOPMENT PLEASE USE dev.sh INSTEAD         !!!!

. env/bin/activate

export FLASK_APP='main.py'
export FLASK_ENV='production'
flask run

deactivate
