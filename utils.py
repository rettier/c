from functools import wraps

import logging
from environs import Env
from flask import request, Response
from werkzeug.exceptions import BadRequest

from storage import FileBackend

env = Env()

logger = logging.getLogger(__name__)


def get_storage_backend():
    backend = env("STORAGE_BACKEND")
    if backend == "file":
        return FileBackend(
            path=env("STORAGE_PATH"),
            cleanup_interval=env.int("CLEANUP_INTERVAL", 5 * 60),
            retention=env("RETENTION", 3600 * 24)
        )
    else:
        logger.error("unknown storage backend {}".format(backend))


def get_key():
    key = request.args.get("c", None).replace(" ", "/").replace("*", "")
    if key is None:
        raise BadRequest()
    return key


def check_auth(auth):
    user, password = env("USERNAME", None), env("PASSWORD", None)
    if not user or not password:
        return True
    else:
        return auth and auth.username == user and auth.password == password


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not check_auth(auth):
            return authenticate()
        return f(*args, **kwargs)

    return decorated
