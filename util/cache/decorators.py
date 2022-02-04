import types
import pickle

from . import base

class Base(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, fn):
        pass


class Memorize(object):
    def __init__(self, arg_selector, cache):
        self.arg_selector = arg_selector
        self.cache = cache

    def __call__(self, fn):
        def wrapper(*args, **kwargs):
            _args = self.arg_selector.select(*args, **kwargs)
            cached = self.cache.get(_args)
            if cached:
                return pickle.loads(cached)
            result = fn(*args, **kwargs)
            self.cache.set(_args, pickle.dumps(result))
            return result

        return wrapper


class ArgSelector(object):
    def select(self, *args, **kwargs):
        return args, kwargs


class PositionSelector(ArgSelector):
    def __init__(self, pos):
        self.pos = pos

    def select(self, *args, **kwargs):
        return args[self.pos]
