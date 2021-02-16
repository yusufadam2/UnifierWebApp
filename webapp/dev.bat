@echo off

cd ./frontend
	call compile.bat
cd ..

cd ./backend
	call ../env/Scripts/activate.bat

	SET FLASK_APP=main.py
	SET FLASK_ENV=development
	flask run

	deactivate
cd ..

