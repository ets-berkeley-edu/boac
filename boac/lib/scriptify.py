"""Execute script functions in an app context."""

from functools import wraps
from boac.factory import create_app


def in_app(func):
    @wraps(func)
    def _in_app_func(*args, **kw):
        app = create_app()
        ac = app.app_context()
        try:
            ac.push()
            kw['app'] = app
            func(*args, **kw)
        finally:
            ac.pop()
    return _in_app_func
