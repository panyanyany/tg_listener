def retry(max_try=3, callback=None, fn=None, args=None, kwargs=None):
    """反复执行 fn，直到没有 exception, 或者尝试次数达到 max_try"""
    def _call_fn(_fn, *_args, **_kwargs):
        result = None
        for i in range(max_try):
            try:
                result = _fn(*_args, **_kwargs)
                break
            except Exception as e:
                if callable(callback):
                    if not callback(i, e):
                        raise
                if i == max_try - 1:
                    raise
        return result

    if fn:
        args = args or []
        kwargs = kwargs or {}
        return _call_fn(fn, *args, **kwargs)

    def replace(*args, **kwargs):
        return _call_fn(*args, **kwargs)

    def wrap():
        return replace

    return wrap
