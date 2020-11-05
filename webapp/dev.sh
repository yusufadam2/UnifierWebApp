#!/bin/sh

source ./common.sh

cd ./frontend
	npm run build
cd ..

cd ./core
	dotnet build
	ASPNETCORE_ENVIRONMENT=Development dotnet ${DOTNET_DEB_DIR}/core.dll
cd ..

