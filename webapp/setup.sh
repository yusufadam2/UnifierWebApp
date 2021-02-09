#!/bin/sh

[ -d ./env ] || python -m venv env

. env/bin/activate

pip3 install -r requirements.txt

deactivate
