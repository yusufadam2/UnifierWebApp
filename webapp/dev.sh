#!/bin/sh

cd ./frontend
	npm run build
cd ..

cd ./backend
	. ../env/bin/activate
	
	export FLASK_APP='main.py'
	export FLASK_ENV='development'
	flask run

	deactivate
cd ..

