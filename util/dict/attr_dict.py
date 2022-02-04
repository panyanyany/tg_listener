

class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class ConstAttrDict(AttrDict):
    __getattr__ = dict.__getitem__

    def __setattr__(self, name, value):
        raise AttributeError("Attribute assignment is forbidden except in __init__")

    def __setitem__(self, name, value):
        raise AttributeError("Item assignment is forbidden")


class IotaAttrDict(AttrDict):

    def __init__(self, args, start=0, step=1):
        kwargs = {}
        i = start
        for arg in args:
            kwargs[arg] = i
            i += step

        super().__init__(kwargs)


class ConstIotaAttrDict(IotaAttrDict, ConstAttrDict): pass
