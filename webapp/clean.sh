#!/bin/sh

cd frontend
	./clean.sh
cd ..

rm -rf ./backend/__pycache__
rm -rf ./publish
rm -rf ./static
