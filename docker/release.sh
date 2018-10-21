#!/usr/bin/env bash
set -e +x

REGISTRY="docker.io"
CACHE_REGISTRY="docker.io"
CONTAINER="rettier/c-server"

# cd to current dir
BASEDIR=$(dirname $0)
pushd $BASEDIR

# bump version
docker run --rm -v "$PWD":/app treeder/bump patch
VERSION=$(cat VERSION)

# build images
./build.sh ${CONTAINER} ${VERSION} ${CACHE_REGISTRY}/${CONTAINER}:latest

# tag images
docker tag ${CONTAINER}:${VERSION} ${REGISTRY}/${CONTAINER}:latest
docker tag ${CONTAINER}:${VERSION} ${REGISTRY}/${CONTAINER}:${VERSION}

# push images to production repo
docker push ${REGISTRY}/${CONTAINER}:latest
docker push ${REGISTRY}/${CONTAINER}:${VERSION}

# print banner
echo "--------------------------------------------------------------------------"
echo "image released to:"
echo "${REGISTRY}/${CONTAINER}:latest"
echo "${REGISTRY}/${CONTAINER}:${VERSION}"
echo "--------------------------------------------------------------------------"
