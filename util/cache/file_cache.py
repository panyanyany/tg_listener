"""文件缓存，即存在文件中"""
import os
from datetime import timedelta, datetime

CACHE_ROOT = 'storage/cache'


class Mode(int):
    pass


class FileCache:
    STRING = Mode(1)
    BYTE = Mode(2)

    def __init__(self, mode: Mode, prefix, max_age=None):
        self.mode = mode
        self.prefix = prefix
        self.max_age = max_age

        prefix_dir_path = os.path.join(CACHE_ROOT, prefix)
        if not os.path.exists(prefix_dir_path):
            os.makedirs(prefix_dir_path)

        if self.max_age:
            for root, dirs, files in os.walk(prefix_dir_path):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    now = datetime.now()
                    if (now.timestamp() - os.stat(filepath).st_mtime) > timedelta(minutes=max_age).total_seconds():
                        os.remove(filepath)
            for root, dirs, files in os.walk(prefix_dir_path):
                for dirname in dirs:
                    dirpath = os.path.join(root, dirname)
                    if len(os.listdir(dirpath)) == 0:
                        os.removedirs(dirpath)

    def save(self, key, content):
        cache_file_path = os.path.join(CACHE_ROOT, self.prefix, key)
        cache_dir_path = os.path.dirname(cache_file_path)

        if not os.path.exists(cache_dir_path):
            os.makedirs(cache_dir_path)

        m = 'w+'
        if self.mode == self.BYTE:
            m = 'w+b'

        with open(cache_file_path, m, encoding='utf8') as fp:
            fp.write(content)

    def exists(self, key):
        cache_file_path = os.path.join(CACHE_ROOT, self.prefix, key)
        return os.path.exists(cache_file_path)

    def load(self, key):
        cache_file_path = os.path.join(CACHE_ROOT, self.prefix, key)

        m = 'r'
        if self.mode == self.BYTE:
            m = 'r+b'

        with open(cache_file_path, m, encoding='utf8') as fp:
            content = fp.read()

        return content
