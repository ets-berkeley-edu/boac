"""Official access to student enrollment data"""

import urllib.parse as urlparse

from boac.lib import http
from boac.lib.mockingbird import fixture
from flask import current_app as app


@fixture('sis_enrollments_api_{cs_id}_{term_id}')
def get_enrollments(cs_id, term_id, mock=None):
    url_components = urlparse.urlparse(app.config['ENROLLMENTS_API_URL'])
    path = url_components.path + '/' + str(cs_id)
    query = {
        'term-id': term_id,
        'primary-only': 'true',
        'page-size': 50,
    }
    url = urlparse.urlunparse([
        url_components.scheme,
        url_components.netloc,
        path,
        '',
        urlparse.urlencode(query, doseq=True),
        '',
    ])
    with mock(url):
        return authorized_request(url)


def authorized_request(url):
    auth_headers = {
        'app_id': app.config['ENROLLMENTS_API_ID'],
        'app_key': app.config['ENROLLMENTS_API_KEY'],
        'Accept': 'application/json',
    }
    return http.request(url, auth_headers)
