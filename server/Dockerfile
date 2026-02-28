FROM python:3.7-alpine

# install base requirements
RUN pip install --no-cache-dir Click==7.0 environs==4.1.0 Flask==1.0.2 gunicorn==19.9.0 itsdangerous==1.1.0 Jinja2==2.10 MarkupSafe==1.1.0 marshmallow==2.17.0 python-dotenv==0.10.1 Werkzeug==0.14.1

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