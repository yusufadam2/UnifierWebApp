@echo off

cd frontend
	clean.bat
cd ..

rmdir /S/Q backend/__pycache__
rmdir /S/Q publish
rmdir /S/Q static
