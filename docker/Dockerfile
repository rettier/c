FROM python:3.7-alpine

# build args
ARG GIT_COMMIT=dev
ARG GIT_COMMIT_SHORT=dev
ARG GIT_BRANCH=dev
ARG VERSION=dev

# install base requirements
RUN pip install --no-cache-dir flask environs gunicorn

ADD server/ /app
WORKDIR /app
CMD ["gunicorn", "main:app"]
