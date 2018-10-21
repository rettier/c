import glob
import os

import logging

logger = logging.getLogger(__name__)


class StorageBackend:
    def __init__(self, retention=None):
        self.retention = retention or 3600 * 24

    def list(self, prefix=""):
        raise NotImplementedError()

    def has_key(self, key):
        raise NotImplementedError()

    def key_is_protected(self, key):
        raise NotImplementedError()

    def put(self, key, stream):
        raise NotImplementedError()

    def get(self, key):
        raise NotImplementedError()


class FileBackend(StorageBackend):
    def __init__(self, path, cleanup_interval, retention):
        super().__init__(retention)
        self.path = path
        self.block_size = 1024 * 1024 * 4
        self.cleanup_interval = cleanup_interval
        if self.cleanup_interval < self.retention:
            logger.warning("Retention duration ({}) lower than cleanup interval ({}). Data may be retained up to "
                           "the cleanup interval.".format(self.retention, self.cleanup_interval))

    def _secure_path(self, path):
        return os.path.normpath('/' + path).lstrip('/')

    def list(self, prefix=""):
        prefix = self._secure_path(prefix)
        return [{
            "path": file,
            "size": os.path.getsize(file),
            "dir": os.path.isdir(file)
        } for file in glob.glob(prefix + "*")]

    def has_key(self, key):
        return os.path.exists(os.path.join(self.path, self._secure_path(key)))

    def key_is_protected(self, key):
        return os.path.basename(key).startswith(".")

    def put(self, key, stream):
        sanitized_key = self._secure_path(key)
        path = os.path.join(self.path, sanitized_key)
        with open(path, "wb") as f:
            while not stream.is_exhausted:
                f.write(stream.read(self.block_size))
        return "saved as {}".format(sanitized_key)

    def get(self, key):
        path = os.path.join(self.path, self._secure_path(key))
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(self.block_size), b''):
                yield block
