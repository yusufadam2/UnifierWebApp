#!/bin/sh

[ -d ./publish ] && rm -rf ./publish/* || mkdir ./publish
mkdir ./publish/{server,static}


cd ./frontend
	npm run build
cd ..

cp -rf ./static/* ./publish/static


cd ./core
	dotnet build --configuration Release
cd ..

cp -rf ./core/bin/Release/netcoreapp3.1/* ./publish/server

