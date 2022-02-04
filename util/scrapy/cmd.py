import sys


def get_scrapy_command():
    if len(sys.argv) == 1:
        cmd = sys.argv[0]
    elif sys.argv[1] == 'crawl':
        cmd = sys.argv[2]
    else:
        cmd = sys.argv[1]
    return cmd
