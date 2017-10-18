"""Official access to student data"""

from boac.lib import http
from boac.lib.mockingbird import fixture
from flask import current_app as app


@fixture('sis_student_api_{cs_id}')
def get_student(cs_id, mock=None):
    url = http.build_url(app.config['STUDENT_API_URL'] + '/' + str(cs_id) + '/all')
    with mock(url):
        return authorized_request(url)


def authorized_request(url):
    auth_headers = {
        'app_id': app.config['STUDENT_API_ID'],
        'app_key': app.config['STUDENT_API_KEY'],
        'Accept': 'application/json',
    }
    return http.request(url, auth_headers)
