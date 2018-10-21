import glob
import gzip
import os

import logging
import stat
import threading
import time

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
        if self.retention < self.cleanup_interval:
            logger.warning("Retention duration ({}) lower than cleanup interval ({}). Data may be retained up to "
                           "the cleanup interval.".format(self.retention, self.cleanup_interval))

        cleanup_thread = threading.Thread(target=self._cleanup_thread)
        cleanup_thread.setDaemon(True)
        cleanup_thread.start()

    def _cleanup_thread(self):
        while True:
            delete_before = time.time() - self.retention
            for file in glob.iglob(os.path.join(self.path + "*"), recursive=True):
                file_stat = os.stat(file)
                if not stat.S_ISDIR(file_stat.st_mode) and file_stat.st_ctime < delete_before:
                    os.remove(file)

            time.sleep(self.cleanup_interval)

    def _secure_path(self, path):
        return os.path.normpath('/' + path).lstrip('/')

    def list(self, prefix=""):
        prefix = os.path.join(self.path, self._secure_path(prefix))
        return [{
            "path": file[len(self.path) + 1:],
            "size": os.path.getsize(file),
            "dir": os.path.isdir(file)
        } for file in glob.glob(prefix + "/*")]

    def has_key(self, key):
        return os.path.exists(os.path.join(self.path, self._secure_path(key)))

    def put(self, key, stream):
        sanitized_key = self._secure_path(key)
        path = os.path.join(self.path, sanitized_key)
        dirname = os.path.dirname(path)

        try:
            os.makedirs(dirname, exist_ok=True)

            with open(path, "wb") as f:
                while not stream.is_exhausted:
                    f.write(stream.read(self.block_size))
        except IsADirectoryError as e:
            return str(e)

        return "saved as {}".format(sanitized_key)

    def get(self, key):
        path = os.path.join(self.path, self._secure_path(key))

        if os.path.isdir(path):
            yield gzip.compress("Is a directory '{}'".format(path).encode("utf-8"))
            return

        with open(path, "rb") as f:
            for block in iter(lambda: f.read(self.block_size), b''):
                yield block
