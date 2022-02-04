import sqlalchemy
import inspect


all_exc = []
for k in dir(sqlalchemy.exc):
    e = getattr(sqlalchemy.exc, k)
    if inspect.isclass(e) and issubclass(e, Exception):
        all_exc.append(e)


def is_sqlalchemy_exception(e):
    return isinstance(e, all_exc)
