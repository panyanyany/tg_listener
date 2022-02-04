import pytest
import unittest

from util.dict import attr_dict


class Base(unittest.TestCase):
    pass


class TestAttrDict(Base):

    def setUp(self):
        self.ad = attr_dict.AttrDict({'a':0, 'b':1})

    def test_item_access(self):
        assert self.ad['a'] is 0
        assert self.ad['b'] is 1

    def test_attr_access(self):
        assert self.ad.a is 0
        assert self.ad.b is 1

    def test_non_exist_attr_access(self):
        with pytest.raises(KeyError):
            self.ad.ax

    def test_attr_assignment(self):
        self.ad.a = 10
        assert self.ad.a is 10

    def test_item_assignment(self):
        self.ad['a'] = 11
        assert self.ad.a is 11

    def test_existence_detect(self):
        assert 'a' in self.ad
        assert 'b' in self.ad

    def test_non_existence_detect(self):
        assert 'ax' not in self.ad
        assert 'bx' not in self.ad


class TestConstAttrDict(TestAttrDict):

    def setUp(self):
        self.ad = attr_dict.ConstAttrDict({'a':0, 'b':1})

    def test_item_assignment(self):
        with pytest.raises(AttributeError):
            super().test_item_assignment()

    def test_attr_assignment(self):
        with pytest.raises(AttributeError):
            super().test_attr_assignment()


class TestIotaAttrDict(TestAttrDict):

    def setUp(self):
        self.ad = attr_dict.IotaAttrDict(['a', 'b'])
        self.ad2 = attr_dict.IotaAttrDict(['a', 'b'], start=1, step=2)

    def test_step(self):

        assert self.ad2.a is 1
        assert self.ad2.b is 3


class TestConstIotaAttrDict(TestIotaAttrDict):

    def setUp(self):
        self.ad = attr_dict.ConstIotaAttrDict(['a', 'b'])
        self.ad2 = attr_dict.ConstIotaAttrDict(['a', 'b'], start=1, step=2)

    def test_item_assignment(self):
        with pytest.raises(AttributeError):
            super().test_item_assignment()

    def test_attr_assignment(self):
        with pytest.raises(AttributeError):
            super().test_attr_assignment()
