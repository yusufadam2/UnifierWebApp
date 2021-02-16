@echo off

rmdir /S/Q __pycache__
rmdir /S/Q tmp
rmdir /S/Q ..\static

mkdir tmp
mkdir ..\static

mkdir tmp\html
mkdir ..\static\html

..\env\Scripts\python.exe build.py .\html\ .\layouts\ .\tmp\ ..\static\

mkdir ..\static\lib
mkdir ..\static\css
mkdir ..\static\js

xcopy lib\* ..\static\lib
xcopy css\* ..\static\css
xcopy js\* ..\static\js

xcopy public\* ..\static

rmdir /S/Q ..\static\layouts
