#!/bin/sh

. common.sh

[ -d ./publish ] && rm -rf ./publish/* || mkdir ./publish
mkdir ./publish/{server,static}


cd ./frontend
	npm run build
cd ..

cp -rf ./static/* ./publish/static


cd ./core
	dotnet build --configuration Release
cd ..

cp -rf ./core/${DOTNET_REL_DIR}/* ./publish/server

