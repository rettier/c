#!/bin/bash

function _c(){
  echo $@
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
    readlink -f $1 | cc
}

function _cr(){
	if tty > /dev/null ; then
	    curl "$C_HOST/?c=$1" -XGET -sS | gunzip
	else
	    gzip <&0 | curl -H 'Content-Type: application/octet-stream' -XPOST --data-binary @- -sS "$C_HOST/?c=$1"
	fi
}

function main(){
    if which -s pbcopy ; then
        COPY=pbcopy
        PASTE=pbpaste
    elif which -s xclip ; then
        COPY=xclip -selection c
        PASTE=xclip -selection clipboard -o
    fi

    COMMAND=$(basename $0)
    COMMANDS=(cc cr cf c)
    if echo ${COMMANDS[@]} | grep -o ${COMMAND} >/dev/null ; then
        COMMAND="_${COMMAND}"
        $COMMAND $@ <&0
    fi
}

C_HOST=${C_HOST:-"https://c.philipp.ninja"}
main $@