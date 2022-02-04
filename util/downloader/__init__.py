# see: https://github.com/gevent/gevent/blob/master/examples/concurrent_download.py
import gevent
import gevent.monkey
import urllib.request
import os
gevent.monkey.patch_all()
import requests

# gevent.monkey.patch_socket()

from gevent import socket
from gevent.pool import Pool


def download_file(url):
    urllib.request.urlopen(url)


def download_requests(url):
    requests.get(url)


def run(fn, args_list, concurrency=10, timeout=100):
    pool = Pool(concurrency)
    with gevent.Timeout(timeout, False):
        jobs = []
        for args in args_list:
            jobs += [pool.spawn(fn, *args)]
        pool.join(timeout, jobs)

