import os
import yaml


ROOT_DIR = '.flag'


class Base(object):
    FLAG_NAME = ''
    contents = {}
    file_type = '.yml'

    def __init__(self, flag_name):
        self.flag_name = flag_name or self.FLAG_NAME
        assert self.flag_name, AttributeError("instance flag_name should not be empty")

        self.load()

    def set(self, key, val):
        self.contents[key] = val
        self.flush()

    def get(self, key):
        return self.contents.get(key)

    def load(self):
        path = self.fullpath()
        if not os.path.exists(path):
            return 
        with open(path) as fp:
            self.contents = yaml.load(fp) or {}

    def fullpath(self):
        path = os.path.join(ROOT_DIR, self.flag_name + self.file_type)
        return path


    def flush(self):
        path = self.fullpath()
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(path, 'w+') as fp:
            yaml.dump(self.contents, fp)
