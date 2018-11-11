#!/bin/bash

# ------------------------------------------------------------------------------
# inlined version of Michael Kropat's (mkropat) realpath.sh
# https://github.com/mkropat/sh-realpath
# this is to get rid of the core-utils dependency on osx
realpath() {
    canonicalize_path "$(resolve_symlinks "$1")"
}

resolve_symlinks() {
    _resolve_symlinks "$1"
}

_resolve_symlinks() {
    _assert_no_path_cycles "$@" || return

    local dir_context path
    path=$(readlink -- "$1")
    if [ $? -eq 0 ]; then
        dir_context=$(dirname -- "$1")
        _resolve_symlinks "$(_prepend_dir_context_if_necessary "$dir_context" "$path")" "$@"
    else
        printf '%s\n' "$1"
    fi
}

_prepend_dir_context_if_necessary() {
    if [ "$1" = . ]; then
        printf '%s\n' "$2"
    else
        _prepend_path_if_relative "$1" "$2"
    fi
}

_prepend_path_if_relative() {
    case "$2" in
        /* ) printf '%s\n' "$2" ;;
         * ) printf '%s\n' "$1/$2" ;;
    esac
}

_assert_no_path_cycles() {
    local target path

    target=$1
    shift

    for path in "$@"; do
        if [ "$path" = "$target" ]; then
            return 1
        fi
    done
}

canonicalize_path() {
    if [ -d "$1" ]; then
        _canonicalize_dir_path "$1"
    else
        _canonicalize_file_path "$1"
    fi
}

_canonicalize_dir_path() {
    (cd "$1" 2>/dev/null && pwd -P)
}

_canonicalize_file_path() {
    local dir file
    dir=$(dirname -- "$1")
    file=$(basename -- "$1")
    (cd "$dir" 2>/dev/null && printf '%s/%s\n' "$(pwd -P)" "$file")
}
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# c macro start
function _c(){
  if [[ $# -gt 0 ]] ; then
      _cr $@ <&0
      return
  fi
  if tty > /dev/null; then
    $PASTE
  else
    $COPY <&0
  fi
}

function _cc(){
  if tty > /dev/null ; then
    $PASTE
  else
    $COPY <&0
    $PASTE
  fi
}

function _cf(){
    if realpath "$1" ; then
      realpath "$1" | c ${@:2} > /dev/null
    fi
}

function _cr(){
    if [[ -z $C_HOST ]] ; then
        echo "missing configuration: set \$C_HOST to a c-server"
        exit 1
    fi

    KEY=$(echo $* | sed "s/ /%20/g")
	if tty > /dev/null ; then
	    curl -G "$C_HOST/?c=$KEY" -XGET -sS | gunzip
	else
	    gzip <&0 | curl -H 'Content-Type: application/octet-stream' -XPOST "$C_HOST/?c=$KEY" --data-binary @- -sS
	fi
}

function has_command() {
    which "$1" >/dev/null 2>&1 
}

function main(){
    if has_command pbcopy ; then
        COPY="pbcopy"
        PASTE="pbpaste"
    elif has_command xclip ; then
        COPY="xclip -selection c"
        PASTE="xclip -selection clipboard -o"
    elif has_command xsel ; then
        COPY="xsel --clipboard --input"
        PASTE="xsel --clipboard --output"
    fi

    COMMAND=$(basename $0)
    COMMANDS=(cc cr cf c)
    if echo ${COMMANDS[@]} | grep -o ${COMMAND} >/dev/null ; then
        COMMAND="_${COMMAND}"
        $COMMAND $@ <&0
    fi
}
# ------------------------------------------------------------------------------

main $@
