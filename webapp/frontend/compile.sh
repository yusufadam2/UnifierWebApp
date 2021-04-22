#!/bin/sh

. ./common.sh

## clear any previously generated assets
./clean.sh

## setup build environment
mkdir ${TMP} ${OUT}

## template files, convert markdown to html, and build post index file
. ../env/bin/activate

mkdir ${TMP}/html ${OUT}/html

python build.py html/ ${LAYOUTS}/ ${TMP}/ ${OUT}/

deactivate

## copy over static files into webroot
mkdir ${OUT}/lib && cp -r lib/* ${OUT}/lib
mkdir ${OUT}/css && cp -r css/* ${OUT}/css
mkdir ${OUT}/js && cp -r js/* ${OUT}/js

cp -r public/* ${OUT}

## clean unnecessary files
rm -rf ${OUT}/layouts ${OUT}/html
