"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


from contextlib import contextmanager
from functools import wraps
import json
import os

from boac.lib.util import fill_pattern_from_args
from flask import current_app as app
import pandas


"""This module stubs SQL-querying functions by a CSV-derived array of dicts in test or demo mode.

A test function can temporarily substitute custom mock behavior with the register_mock context manager.
"""


class MockRows:
    """A callable object which uses a CSV file or list of strings to mimic data rows from a non-ORM SQL query."""

    def __init__(self, csv_in):
        self.csv_in = csv_in

    def __call__(self, *args):
        if self.csv_in is None:
            return None
        # Unless otherwise instructed, `pandas` will interpret numeric strings as numbers instead of strings.
        df = pandas.read_csv(self.csv_in, dtype={'ldap_uid': object, 'sis_section_num': object, 'uid': object})
        # `pandas` also likes to store its numbers as numpy.int64, which is not JSON serializable, so we have
        # to pipe the dataframe through JSON conversion before returning.
        result = json.loads(df.to_json(None, 'records'))
        # Be kind, rewind.
        if hasattr(self.csv_in, 'seek'):
            self.csv_in.seek(0)
        return result


"""Registry associating mockable request functions with zero or more mock responses. Responses are arranged
in a last-in-first-out queue so that test code can temporarily substitute custom mocks."""
_mock_registry = {}


def _register_mock(request_function, response_function):
    _mock_registry[request_function.__name__].append(response_function)


def _unregister_mock(request_function):
    _mock_registry[request_function.__name__].pop()


def mockable(func):
    """Mark function as mockable.

    If mocking is in effect, the decorated function will not be called. Instead, the mock response will be returned.
    """
    _mock_registry[func.__name__] = []

    @wraps(func)
    def mockable_wrapper(*args, **kw):
        if _environment_supports_mocks() and _mock_registry.get(func.__name__):
            mock_response = _mock_registry[func.__name__][-1](*args, **kw)
            if isinstance(mock_response, MockRows):
                return mock_response()
        return func(*args, **kw)
    return mockable_wrapper


def mocking(request_func):
    r"""Mark function as returning mock response.

    The function to be mocked should be supplied to the decorator as an argument. The decorated function will be called
    with the same arguments as the function to be mocked and may generate a dynamic response.

    Usage:

    @mocking(query_external_db)
    def external_db_mock():
        return MockRows(io.StringIO('uid,canvas_user_id,loch_page_views\n2040,99999,13'))
    """
    @wraps(request_func)
    def register_mock_for_request_func(func):
        if _environment_supports_mocks():
            _register_mock(request_func, func)
        return func
    return register_mock_for_request_func


def fixture(pattern):
    """Alternative to @mockable, @mocking, and response_from_fixture.

    The @fixture decorator with a template pattern can be used as a shorthand. Wrapping a function like so:

    @fixture('resource_{resource_id}_rows.csv')
    def query_external_db(resource_id):
        ...

    is equivalent to specifying paired @mockable and @mocking functions:

    @mockable
    def query_external_db(resource_id):
        ...

    @mocking(query_external_db)
    def external_db_mock(resource_id):
        return response_from_fixture(f'resource_{resource_id}_rows.csv')
    """
    def fixture_wrapper(func):
        def register_fixture(*args, **kw):
            evaluated_pattern = fill_pattern_from_args(pattern, func, *args, **kw)
            return response_from_fixture(evaluated_pattern)

        mockable_wrapper = mockable(func)
        mocking(func)(register_fixture)
        return mockable_wrapper

    return fixture_wrapper


def response_from_fixture(pattern):
    """Generate a mock response from a fixture filename.

    The CSV-parsed fixture data will replace the original function's response. None will be returned
    if the fixture is not found.

    Usage:

    @mocking(query_external_db)
    def external_db_mock(resource_id):
        return response_from_fixture(f'resource_{resource_id}_rows.csv')
    """
    fixture_path = f'{_get_fixtures_path()}/{pattern}'
    if os.path.isfile(fixture_path):
        return MockRows(fixture_path)
    else:
        return MockRows(None)


@contextmanager
def register_mock(request_function, response):
    """Context manager, intended to be used from tests, that temporarily registers a mock response for a given request.

    A MockRows object may be supplied, or, if dynamic behavior is required, a function that returns a MockRows.
    """
    if isinstance(response, MockRows):
        response_function = lambda *args: response
    else:
        response_function = response
    _register_mock(request_function, response_function)
    try:
        yield
    finally:
        _unregister_mock(request_function)


# It would be nicer to use a MOCKS_ENABLED config value rather than a hardcoded list of environments, but tests are
# currently set up such that this code is loaded before app config is in place.
def _environment_supports_mocks():
    env = os.environ.get('BOAC_ENV')
    return env == 'test' or env == 'demo'


def _get_fixtures_path():
    return app.config.get('FIXTURES_PATH') or (app.config['BASE_DIR'] + '/fixtures')
