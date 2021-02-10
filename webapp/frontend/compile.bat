@echo off

clean.bat

mkdir tmp ../static

../env/bin/activate.bat

mkdir tmp/html ../static/html

python build.py html/ layouts/ tmp/ ../static/

deactivate

mkdir ../static/lib
mkdir ../static/css
mkdir ../static/js

cp lib/* ../static/lib
cp css/* ../static/css
cp js/* ../static/js

cp public/* ../static

rmdir /S/Q ../static/layouts
