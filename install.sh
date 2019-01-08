#!/bin/bash

has_command() {
    command -v "$1" >/dev/null 2>&1
}

get_latest_release() {
  wget -q -O- "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

install_osx(){
    if has_command "brew" ; then
        brew install rettier/tap/c
    else
        echo "Please install Homebrew first"
        echo "https://brew.sh/"
        exit 1
    fi
}

install_debian(){
    wget "https://github.com/rettier/c/releases/download/${version}/c_${version:1}.deb" -q -O c.deb
    $run_sudo dpkg -i c.deb >/dev/null
}

install_linux_common(){
    wget "https://github.com/rettier/c/releases/download/${version}/c_${version:1}.tar.gz" -q -O c.tar.gz
    tar -xf c.tar.gz
    mv c_${version:1}/* /usr/bin/
}

install_linux(){
    tempdir="$(mktemp -d)"
    pushd "${tempdir}" >/dev/null
    version=$(get_latest_release "rettier/c")
    run_sudo=''
    if (( $EUID != 0 )); then
        run_sudo='sudo'
    fi

    if has_command "dpkg" ; then
        install_debian "${version}"
    else
        install_linux_common "${version}"
    fi
    rm -r "${tempdir}"
}

case "$(uname -s)" in
    Linux*)     install_linux;;
    Darwin*)    install_osx;;
    *)          echo "Unknown OS, exiting..."; exit 1;;
esac


