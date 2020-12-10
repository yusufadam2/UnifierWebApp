#!/bin/sh

[ -d ./env ] || python -m venv env

. env/bin/activate

pip install -r requirements.txt

deactivate
