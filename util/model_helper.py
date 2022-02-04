# -*- coding: utf-8 -*-
from util import inspect_util


class Model:
    def __repr__(self):
        fields = inspect_util.get_custom_properties(self)
        pairs = []
        for f in fields:
            pairs.append("%s=%r" % (f, getattr(self, f)))
        msg = "%s(%s)" % (self.__class__.__name__, ', '.join(pairs))
        return msg

    def to_dict(self):
        d = {}
        fields = inspect_util.get_custom_properties(self)
        for f in fields:
            v = getattr(self, f)
            if hasattr(v, 'to_dict') and isinstance(self, Model):
                v = v.to_dict()
            d[f] = v
        return d

    @classmethod
    def from_dict(cls, d):
        self = cls()
        if '__annotations__' in self.__class__.__dict__:
            annotations = self.__class__.__dict__['__annotations__']
        else:
            annotations = {}
        fields = inspect_util.get_custom_properties(self)
        for f in fields:
            ptype = annotations.get(f)
            if hasattr(ptype, 'from_dict') and issubclass(ptype, Model):
                setattr(self, f, ptype.from_dict(d[f]))
            else:
                setattr(self, f, d[f])
        return self
