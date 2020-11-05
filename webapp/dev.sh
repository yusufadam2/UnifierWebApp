#!/bin/sh

cd ./frontend
	npm run build
cd ..

cd ./core
	dotnet build
	dotnet bin/Debug/netcoreapp3.1/core.dll
cd ..

