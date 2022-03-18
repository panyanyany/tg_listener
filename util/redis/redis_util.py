import pickle

from redis import Redis


class RedisUtil:
    def __init__(self, rdb: Redis = None, prefix=''):
        self.rdb = rdb or Redis(host='localhost', port=6379, db=0)
        self.prefix = prefix

    def exists(self, key):
        if self.prefix:
            key = self.prefix + ':' + key
        return self.rdb.exists(key)

    def set(self, key, val):
        if self.prefix:
            key = self.prefix + ':' + key
        return self.rdb.set(key, pickle.dumps(val))

    def get(self, key):
        if self.prefix:
            key = self.prefix + ':' + key
        val = self.rdb.get(key)
        if val is None:
            return val
        return pickle.loads(val)
