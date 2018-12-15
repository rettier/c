import logging
from functools import wraps

from environs import Env
from flask import request, Response
from storage import FileBackend
from werkzeug.exceptions import BadRequest

env = Env()

logger = logging.getLogger(__name__)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_storage_backend():
    backend = env("STORAGE_BACKEND")
    if backend == "file":
        return FileBackend(
            path=env("STORAGE_PATH"),
            cleanup_interval=env.int("CLEANUP_INTERVAL", 5 * 60),
            retention=env("RETENTION", None)
        )
    else:
        logger.error("unknown storage backend {}".format(backend))


def get_key():
    key = request.args.get("c", "").replace(" ", "/").replace("*", "")
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
