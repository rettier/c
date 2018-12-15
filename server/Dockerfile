FROM python:3.7-alpine

# install base requirements
RUN pip install --no-cache-dir flask environs gunicorn

ADD src/ /app
WORKDIR /app
CMD ["gunicorn", "main:app", "-w", "4", "--threads", "12", "--bind", "0.0.0.0:80"]

# documentation
ARG GIT_COMMIT=dev
ARG GIT_BRANCH=dev
ARG VERSION=dev
ENV GIT_COMMIT=${GIT_COMMIT} \
    GIT_BRANCH=${GIT_BRANCH} \
    VERSION=${VERSION}