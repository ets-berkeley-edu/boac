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


def in_session_request(func):
    """Flask-SQLAlchemy requires a request context to do any DB work."""
    @wraps(func)
    def _in_session_request_func(*args, **kw):
        request_ctx = None
        app = create_app()
        ac = app.app_context()
        try:
            ac.push()
            request_ctx = app.test_request_context('/')
            request_ctx.push()
            kw['app'] = app
            func(*args, **kw)
        finally:
            if request_ctx:
                request_ctx.pop()
            ac.pop()
    return _in_session_request_func
