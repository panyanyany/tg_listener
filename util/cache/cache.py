import os
import random
import json
import urllib
import hashlib
import pickle

from . import storage


class Base:
    storage = None
    keygen = None

    def __init__(self, storage=None, keygen=str, **kwargs):
        self.storage = storage
        self.keygen = keygen

    def set(self, *args, **kwargs):
        raise NotImplementedError
    def get(self, *args, **kwargs):
        raise NotImplementedError


class KeyValueCache(Base):
    storage = None
    keygen = None

    def _keygen(self, key):
        if self.keygen:
            key = self.keygen(key)
        else:
            key = str(key)
        return key

    def set(self, key, value):
        return self.storage.set(self._keygen(key), value)

    def get(self, key):
        return self.storage.get(self._keygen(key))


class DirectoryCache(KeyValueCache):
    def __init__(self, cache_dir='data', **kwargs):
        super().__init__(**kwargs)
        self.storage = storage.Directory(self)
        self.cache_dir = cache_dir
