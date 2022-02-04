# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

import unittest

"""
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(THIS_DIR, '..')
SEARCH_DIR = os.path.join(THIS_DIR, '../..')

sys.path.insert(0, SEARCH_DIR)
"""

from util.tests.hooks import df_decoraters as df


class TestBase(unittest.TestCase):

    def setUp(self):
        pass

    def load(self, rel_path):
        """load file by relative path"""
        return ""


class TestDecoraters(TestBase):

    def test_return_hooks(self):
        df.test_return_hooks()

       
def main():
    unittest.main()


if __name__ == '__main__':
    main()

