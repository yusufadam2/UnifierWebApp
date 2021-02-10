@echo off

cd ./frontend
	compile.bat
cd ..

cd ./backend
	../env/bin/activate.bat

	SET FLASK_APP=main.py
	SET FLASK_ENV=development
	flask run

	deactivate
cd ..

