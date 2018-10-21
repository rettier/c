import gzip

from environs import Env
from flask import Flask, request, Response

from utils import requires_auth, get_storage_backend, get_key, sizeof_fmt

env = Env()
app = Flask(__name__)
empty_gzip = b"\x1f\x8b\x08\x00\x50\xac\xc3\x5b\x00\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00"
storage_backend = get_storage_backend()


@app.route("/", methods=["POST"])
@requires_auth
def post():
    return storage_backend.put(get_key(), request.stream)


def ll(*args):
    files = storage_backend.list(prefix="/".join(args))
    dirs = sorted(filter(lambda x: x["dir"], files), key=lambda x: x["path"])
    files = sorted(filter(lambda x: not x["dir"], files), key=lambda x: x["path"])

    result = ""
    for dir in dirs:
        result += "   (dir) {path}\n".format(**dir)

    for file in files:
        human_size = sizeof_fmt(file["size"])
        result += "{human_size:>8} {path}\n".format(human_size=human_size, **file)

    return result


def ls(*args):
    files = storage_backend.list(prefix="/".join(args))
    dirs = sorted(filter(lambda x: x["dir"], files), key=lambda x: x["path"])
    files = sorted(filter(lambda x: not x["dir"], files), key=lambda x: x["path"])
    return " ".join([x["path"] + "/" for x in dirs] + [x["path"] for x in files])


commands = {
    "ls": ls,
    "ll": ll
}


def process_custom_command(key):
    command, *args = [x.strip() for x in key.split("/")]
    print(command, args)
    if command not in commands:
        return False
    result = commands[command](*args)
    return result


@app.route("/", methods=["GET"])
@requires_auth
def get():
    key = get_key()
    result = process_custom_command(key)

    if result is False:
        if storage_backend.has_key(key):
            result = storage_backend.get(key)
        else:
            result = empty_gzip

    if isinstance(result, str):
        result = gzip.compress(result.encode("utf-8"))

    return Response(result, content_type="application/octet-stream")


if __name__ == "__main__":
    app.run(
        host=env("HOST", "localhost"),
        port=env.int("PORT", 8099),
        debug=env.bool("DEBUG", False)
    )
