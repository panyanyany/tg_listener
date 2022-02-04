import os


class Base:
    def __init__(self, cache):
        self.cache = cache


class Directory(Base):
    def getFullPath(self, path):
        return os.path.join(self.cache.cache_dir, path)

    def makeDirAvailable(self, path):
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def set(self, path, value):
        fullpath = self.getFullPath(path)
        self.makeDirAvailable(fullpath)
        with open(fullpath, 'w+') as fp:
            fp.write(value)

    def get(self, path):
        fullpath = self.getFullPath(path)
        if not os.path.exists(fullpath):
            return None
        with open(fullpath) as fp:
            return fp.read()
