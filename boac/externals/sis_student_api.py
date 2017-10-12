"""Official access to student data"""

import urllib.parse as urlparse

from boac.lib import http
from boac.lib.mockingbird import fixture
from flask import current_app as app


@fixture('sis_student_api_{cs_id}')
def get_student(cs_id, mock=None):
    url_components = urlparse.urlparse(app.config['STUDENT_API_URL'])
    path = url_components.path + '/' + str(cs_id) + '/all'
    url = urlparse.urlunparse([
        url_components.scheme,
        url_components.netloc,
        path,
        '',
        '',
        '',
    ])
    with mock(url):
        return authorized_request(url)


def authorized_request(url):
    auth_headers = {
        'app_id': app.config['STUDENT_API_ID'],
        'app_key': app.config['STUDENT_API_KEY'],
        'Accept': 'application/json',
    }
    return http.request(url, auth_headers)
