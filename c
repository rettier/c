#!/bin/bash

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
    if $READLINK -f $1 ; then
        $READLINK -f $1 | c ${@:2} > /dev/null
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

function main(){
    if which pbcopy > /dev/null ; then
        COPY="pbcopy"
        PASTE="pbpaste"
        READLINK="greadlink"
    elif which xclip > /dev/null ; then
        COPY="xclip -selection c"
        PASTE="xclip -selection clipboard -o"
        READLINK="readlink"
    fi

    COMMAND=$(basename $0)
    COMMANDS=(cc cr cf c)
    if echo ${COMMANDS[@]} | grep -o ${COMMAND} >/dev/null ; then
        COMMAND="_${COMMAND}"
        $COMMAND $@ <&0
    fi
}

main $@