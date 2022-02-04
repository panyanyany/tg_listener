from datetime import timedelta

import requests


# import requests_cache

# requests_cache.install_cache('.requests_cache', allowable_codes=[200, 301, 302, 307])
# requests_cache.install_cache('.requests_cache', expire_after=timedelta(days=1), allowable_codes=[200, 301, 302, 307])


def get(*args, **kwargs):
    headers = kwargs.get('headers', {})
    headers.setdefault('User-Agent',
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36")
    kwargs['headers'] = headers

    return requests.get(*args, **kwargs)


def post(*args, **kwargs):
    headers = kwargs.get('headers', {})
    headers.setdefault('User-Agent',
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36")
    kwargs['headers'] = headers

    return requests.post(*args, **kwargs)
