"""Official access to student enrollment data"""

from boac.lib import http
from boac.lib.mockingbird import fixture
from flask import current_app as app


@fixture('sis_enrollments_api_{cs_id}_{term_id}')
def get_enrollments(cs_id, term_id, mock=None):
    query = {
        'term-id': term_id,
        'primary-only': 'true',
        'page-size': 50,
    }
    url = http.build_url(app.config['ENROLLMENTS_API_URL'] + '/' + str(cs_id), query)
    with mock(url):
        return authorized_request(url)


def authorized_request(url):
    auth_headers = {
        'app_id': app.config['ENROLLMENTS_API_ID'],
        'app_key': app.config['ENROLLMENTS_API_KEY'],
        'Accept': 'application/json',
    }
    return http.request(url, auth_headers)
