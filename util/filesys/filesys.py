import os
import re


def mkdirs(dir_or_file_path, is_file=False):
    if is_file:
        dir_or_file_path = os.path.dirname(dir_or_file_path)

    if not os.path.exists(dir_or_file_path):
        os.makedirs(dir_or_file_path)


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value)
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    # ...
    return value
