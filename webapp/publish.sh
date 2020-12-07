#!/bin/sh

[ -d ./publish ] && rm -rf ./publish/* || mkdir ./publish
mkdir ./publish/server ./publish/static

cd ./frontend
	npm run build
cd ..

cp -rf ./static/* ./publish/static

cp -rf ./backend/* ./publish/server

cp run.sh ./publish/server

