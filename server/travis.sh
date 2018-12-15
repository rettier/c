#!/bin/bash

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

CONTAINER="rettier/c-server"
VERSION=${TRAVIS_TAG:1}
CACHE_CONTAINER="rettier/c:$TRAVIS_BRANCH"

echo "Building   ${CONTAINER}:${VERSION}"
echo "Cache from ${CACHE_CONTAINER}"

docker pull ${CACHE_CONTAINER} || true
docker build  \
        -f Dockerfile  \
        -t ${CONTAINER}:${VERSION} \
        --cache-from=$CACHE_CONTAINER \
        --build-arg GIT_BRANCH="${TRAVIS_BRANCH}" \
        --build-arg GIT_COMMIT="${TRAVIS_COMMIT}" \
        --build-arg VERSION="${VERSION}" .

docker push ${CONTAINER}:${VERSION}

if [[ $TRAVIS_BRANCH == 'master' ]] ; then
  echo "Pushing additional tag: latest"

  docker tag ${CONTAINER}:${VERSION} ${CONTAINER}:latest
  docker push ${CONTAINER}:latest
fi