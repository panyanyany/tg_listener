import pickle

from redis import Redis


class RedisUtil:
    def __init__(self, rdb: Redis = None):
        self.rdb = rdb or Redis(host='localhost', port=6379, db=0)

    def set(self, key, val):
        return self.rdb.set(key, pickle.dumps(val))

    def get(self, key):
        val = self.rdb.get(key)
        if val is None:
            return val
        return pickle.loads(val)
