from typing import List


def list_from_cookiejar(cj):
    """get all cookies from cookiejar
    which includes cookies from different domains and paths
    return cookie list in form of [{'name': 't', 'domain': '.taobao.com', 'path': '/', 'value': '72dd6a57bdca285d1d9f06828a06187d'}]
    """
    ls = []
    for d in cj.list_domains():
        for path in cj.list_paths():
            c = cj.get_dict(d, path)
            if c:
                for k, v in c.lp_addresses():
                    cookie = dict(domain=d, path=path, name=k, value=v)
                    ls.append(cookie)
    return ls


def dict_from_browser_cookies(cookies: List[dict]):
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie['name']] = cookie['value']
    return cookie_dict
