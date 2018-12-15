#!/usr/bin/env bash
set -e +x

# cd to current dir
BASEDIR=$(dirname $0)
pushd $BASEDIR

VERSION=${TRAVIS_TAG:1}
PKG_NAME="c"

# build tar gz
CHROOT="${PKG_NAME}_${VERSION}"
mkdir -p "$CHROOT"
cp c "$CHROOT/c"
ln -fs "./c" "$CHROOT/cf"
tar czvf "${CHROOT}.tar.gz" "${CHROOT}"
rm -rf "$CHROOT"

# build dpkg
CHROOT="${PKG_NAME}_${VERSION}"
mkdir -p "$CHROOT/usr/local/bin"
mkdir -p "$CHROOT/DEBIAN"
cp control "$CHROOT/DEBIAN/"
cp c "$CHROOT/usr/local/bin/c"
ln -fs "./c" "$CHROOT/usr/local/bin/cf"
dpkg --build "$CHROOT"
rm -rf "$CHROOT"

