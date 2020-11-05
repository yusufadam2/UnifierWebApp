#!/bin/sh

cd ./frontend
	npm run build
cd ..

cd ./core
	dotnet build --configuration Release
	dotnet bin/Release/netcoreapp3.1/core.dll
cd ..

