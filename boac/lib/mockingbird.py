from contextlib import contextmanager
from functools import partial, wraps
import httpretty
import os

from flask import current_app

"""This module wraps the httpretty package to return fake external API responses in test or demo mode.

A module can define mock behavior by using the @mockable decorator on a function that calls an external URL, and the
@mocking decorator on a function that returns the fake response.

A test function can temporarily substitute custom mock behavior with the register_mock context manager.
"""


class MockResponse:
    """A callable object that can be passed into httpretty's register_uri method with the 'body' keyword. (Despite
    that keyword's name, it takes a tuple including status and headers as well as response body.)

    Functions that use the @mocking decorator should return a MockResponse object.

    The register_mock context manager may pass in a MockResponse object, or, if dynamic behavior is required, a function
    that returns a MockResponse object.
    """
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    def __call__(self, *args):
        return (self.status, self.headers, self.body)


"""Registry associating mockable request functions with zero or more mock response functions. Responses are arranged
in a last-in-first-out queue so that test code can temporarily substitute custom mocks."""
_mock_registry = {}


def _register_mock(request_function, response_function):
    _mock_registry[request_function.__name__].append(response_function)


def _unregister_mock(request_function):
    _mock_registry[request_function.__name__].pop()


def mockable(func):
    """Decorator marking a function as mockable. Since httpretty registers mock responses against URLs, the function
    to be decorated must generate (or have access to) the complete URL to be called.

    Functions using this decorator should accept an optional 'mock' argument. The decorator will replace this argument
    with a context manager that activates the mock response currently associated to the mockable function in the
    registry.

    Usage:

    @mockable
    def call_external_api(hostname, resource_id, mock=None):
        ...
        url = 'http://{}/resource/{}'.format(hostname, resource_id)
        ...
        with mock(url):
            response = requests.get(url)
            ...
    """
    _mock_registry[func.__name__] = []

    @wraps(func)
    def mockable_wrapper(*args, **kw):
        if _environment_supports_mocks() and _mock_registry.get(func.__name__):
            mock_response = _mock_registry[func.__name__][-1](*args, **kw)
            kw['mock'] = partial(_activate_mock, mock_response=mock_response)
        else:
            kw['mock'] = _noop_mock
        return func(*args, **kw)
    return mockable_wrapper


def mocking(request_func):
    """Decorator marking a function that returns a mock response. The function to be mocked should be supplied to the
    decorator as an argument. The decorated function will be called with the same arguments as the function to be
    mocked (apart from the optional 'mock' argument) and may generate a dynamic response.

    Usage:

    @mocking(call_external_api)
    def external_api_mock(hostname, resource_id):
        return MockResponse(200, {}, json.dumps({'id': resource_id}))
    """
    @wraps(request_func)
    def register_mock_for_request_func(func):
        if _environment_supports_mocks():
            _register_mock(request_func, func)
        return func
    return register_mock_for_request_func


def fixture(fixture_file):
    """Convenience function to generate a mock response from a fixture filename. If a matching fixture is found, return
    200 with the fixture body. If a matching fixture is not found, return a generic 404.

    Usage:

    @mocking(call_external_api)
    def external_api_mock(hostname, resource_id):
        return fixture('resource_{}_feed.json'.format(resource_id))
    """
    path = current_app.config['BASE_DIR'] + '/../fixtures/{}'.format(fixture_file)
    try:
        file = open(path)
    except FileNotFoundError:
        return MockResponse(404, {}, '{"message": "The requested resource was not found."}')
    with file:
        fixture = file.read()
        return MockResponse(200, {}, fixture)


@contextmanager
def register_mock(request_function, response):
    """Context manager, intended to be used from tests, that temporarily registers a mock response for a given request.
    A MockResponse object may be supplied, or, if dynamic behavior is required, a function that returns a MockResponse."""
    if isinstance(response, MockResponse):
        response_function = lambda *args: response
    else:
        response_function = response

    _register_mock(request_function, response_function)
    yield
    _unregister_mock(request_function)


@contextmanager
def _activate_mock(url, mock_response):
    if mock_response and _environment_supports_mocks():
        httpretty.enable()
        # TODO handle methods other than GET
        httpretty.register_uri(httpretty.GET, url, body=mock_response)
        yield
        httpretty.disable()
    else:
        yield


# It would be nicer to use a MOCKS_ENABLED config value rather than a hardcoded list of environments, but tests are
# currently set up such that this code is loaded before app config is in place.
def _environment_supports_mocks():
    env = os.environ.get('BOAC_ENV')
    return (env == 'test' or env == 'demo')


@contextmanager
def _noop_mock(url):
    yield None
