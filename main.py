import gzip

from environs import Env
from flask import Flask, request, Response

from utils import requires_auth, get_storage_backend, get_key

env = Env()
app = Flask(__name__)
empty_gzip = "\x1f\x8b\x08\x00\x50\xac\xc3\x5b\x00\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00"
storage_backend = get_storage_backend()


@app.route("/", methods=["POST"])
@requires_auth
def post():
    return storage_backend.put(get_key(), request.stream)


def is_ls(key):
    return key[0:2] == "ls" and (len(key) == 2 or key[3] == "/")


def ls(key):
    return gzip.compress(str().encode("ascii"))


@app.route("/", methods=["GET"])
@requires_auth
def get():
    key = get_key()
    if is_ls(key):
        data = ls(key)
    else:
        data = storage_backend.get(key)

    return Response(data, content_type="application/octet-stream")


if __name__ == "__main__":
    app.run(
        host=env("HOST", "localhost"),
        port=env.int("PORT", 8099),
        debug=env.bool("DEBUG", False)
    )
