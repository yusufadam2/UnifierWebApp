#!/bin/bash

ROOT="$(pwd)"
LAYOUTS="${ROOT}/html/layouts"
OUT="${ROOT}/../static"

## $1 : Source folder
## $2 : Destination folder
## $3 : Whitelisted files (glob)
## $4 : Processing functiont to invoke for each file found
##      $1 : Source file
##      $2 : Destination file
FOR_FILES () {
        local SRC="${1}"
        local DST="${2}"
        local GLOB="${3}"
        local FUNC="${4}"

	local OLD="$(pwd)"
	cd "${SRC}"
        find -name "${GLOB}" -type f -print0 | while read -d $'\0' FILE; do
                mkdir -p $(dirname "${DST}/${FILE}") && \
                        "${FUNC}" "${FILE}" "${DST}/${FILE}"
        done
        cd "${OLD}"
}

## $1 : Template file
## $2 : Placeholder string
## $3 : Source file
## $4 : Destination file
TEMPLATE () {
        local TEMPLATE="${1}"
        local PLACEHOLDER="${2}"
        local SRC="${3}"
        local DST="${4}"

        local OPTS="/${PLACEHOLDER}/r ${SRC}"
        sed "${OPTS}" "${TEMPLATE}" | sed "s/${PLACEHOLDER}//g" > "${DST}"
}

## $1 : Source file
## $2 : Destination file
TEMPLATE_LAYOUT () {
        TEMPLATE "${LAYOUTS}/_Layout.html" 'PLACEHOLDER' "${1}" "${2}"
}

## $1 : Source file
## $2 : Destination file
## $3 : Stripped characters
COLLAPSE () {
        local SRC="${1}"
        local DST="${2}"
        local STRIPPED_CHARS="${3}"
        local TMP=$(mktemp)

        cat "${SRC}" | tr -d "${STRIPPED_CHARS}" > "${TMP}"
        cat "${TMP}" > "${DST}"

        rm "${TMP}"
}

## $1 : Source file
## $2 : Destination file
COLLAPSE_MILD () {
        COLLAPSE "${1}" "${2}" '\r\t'
}

## $1 : Source file
## $2 : Destination file
COLLAPSE_STRICT () {
        COLLAPSE "${1}" "${2}" '\n\r\t'
}

[ -d "${OUT}" ] && rm -rf "${OUT}/*" || mkdir "${OUT}"

FOR_FILES "${ROOT}/html" "${OUT}" "*.html" TEMPLATE_LAYOUT
FOR_FILES "${ROOT}/css" "${OUT}/css" "*.css" cp
FOR_FILES "${ROOT}/js" "${OUT}/js" "*.js" cp
#FOR_FILES "${ROOT}/lib" "${OUT}/lib" "*" cp
FOR_FILES "${ROOT}/public" "${OUT}" "*" cp

#FOR_FILES "${OUT}" "${OUT}" "*.html" COLLAPSE_MILD
#FOR_FILES "${OUT}" "${OUT}" "*.css" COLLAPSE_STRICT
#FOR_FILES "${OUT}" "${OUT}" "*.js" COLLAPSE_STRICT

rm -rf "${OUT}/layouts"
