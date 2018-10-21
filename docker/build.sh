#!/usr/bin/env bash
set -ex

CONTAINER=$1
VERSION=$2

GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_COMMIT=$(git rev-parse HEAD)
GIT_COMMIT_SHORT=$(echo ${GIT_COMMIT} | head -c 8)

if ! [[ -z $3 ]] ; then
    CACHELINE="--cache-from ${3}"
    docker pull ${3} || true
fi

docker build  \
        -f Dockerfile  \
        ${CACHELINE:-} \
        -t ${CONTAINER}:${VERSION} \
        --build-arg GIT_BRANCH="$GIT_BRANCH" \
        --build-arg GIT_COMMIT="$GIT_COMMIT" \
        --build-arg GIT_COMMIT_SHORT="$GIT_COMMIT_SHORT" \
        --build-arg VERSION="$VERSION" ..
