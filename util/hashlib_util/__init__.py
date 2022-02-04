import hashlib


def md5(s, encoding='utf8'):
    b = bytes(s, encoding=encoding)
    return hashlib.md5(b).hexdigest()
