#!/bin/sh

./clean.sh

[ -d ./publish ] && rm -r ./publish
mkdir ./publish ./publish/server ./publish/static

cd ./frontend
	npm run build
cd ..

cp -rf ./static/* ./publish/static

cp -rf ./backend/* ./publish/server

## copy server run script
cp run.sh ./publish/server

## setup virtual env for server
cd ./publish/server
	cp ../../requirements.txt ../../setup.sh ./

	./setup.sh
cd ../..
