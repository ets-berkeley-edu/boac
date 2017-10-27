"""Official access to student enrollment data"""

from boac.lib import http
from boac.lib.mockingbird import fixture
from boac.models.json_cache import stow
from flask import current_app as app


@stow('sis_enrollments_api_{cs_id}_{term_id}', for_term=True)
def get_enrollments(cs_id, term_id):
    response = _get_enrollments(cs_id, term_id)
    if response and hasattr(response, 'json'):
        return response.json().get('apiResponse', {}).get('response', {})
    else:
        if hasattr(response, 'raw_response') and response.raw_response.status_code == 404:
            return False
        else:
            return None


@fixture('sis_enrollments_api_{cs_id}_{term_id}')
def _get_enrollments(cs_id, term_id, mock=None):
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
