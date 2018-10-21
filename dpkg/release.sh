#!/usr/bin/env bash
set -e +x

# cd to current dir
BASEDIR=$(dirname $0)
pushd $BASEDIR

# bump version
echo $(awk '{print $1+1}' < REVISION) > REVISION
VERSION=$(cat VERSION)
REVISION=$(cat REVISION)
PKG_NAME="c"
CHROOT="${PKG_NAME}_${VERSION}-${REVISION}"

mkdir -p "$CHROOT/usr/local/bin"
mkdir -p "$CHROOT/DEBIAN"
cp control "$CHROOT/DEBIAN/"
cp ../c "$CHROOT/usr/local/bin/c"
dpkg --build "$CHROOT"
rm -rf "$CHROOT"
