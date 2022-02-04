import pytest
import unittest

from util.dict import attr_dict
from util.model_helper import Model


class Base(unittest.TestCase):
    pass


class NoAnnotationModel(Model):
    a = 0


class SimpleModel(Model):
    a: int = 0
    b: str = ''


class NestedModel(Model):
    nested: SimpleModel = None
    c: int = 0


class TestModel(Base):
    def test_no_annotation_model(self):
        m = NoAnnotationModel.from_dict(dict(a=1))
        assert m.a == 1

    def test_simple_model(self):
        m = SimpleModel.from_dict(dict(a=1, b='2'))
        assert m.a == 1
        assert m.b == '2'

    def test_nested_model(self):
        m = NestedModel.from_dict(dict(c=3, nested=dict(a=1, b='2')))
        assert m.c == 3
        assert m.nested.a == 1
        assert m.nested.b == '2'
