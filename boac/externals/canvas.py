import urllib

from boac.lib import http
from boac.lib.mockingbird import fixture, mockable, mocking


@mockable
def get_user_for_sis_id(canvas_instance, sis_id, mock=None):
    url = build_url(canvas_instance, '/api/v1/users/sis_user_id:UID:{}'.format(sis_id))
    auth_headers = {'Authorization': 'Bearer {}'.format(canvas_instance.token)}
    with mock(url):
        return http.request(url, auth_headers)


@mocking(get_user_for_sis_id)
def get_user_for_sis_id_fixture(canvas_instance, sis_id):
    return fixture('canvas_user_for_sis_id_{}.json'.format(sis_id))


def build_url(canvas_instance, path):
    return urllib.parse.urlunparse([
        canvas_instance.scheme,
        canvas_instance.domain,
        urllib.parse.quote(path),
        '',
        '',
        ''
    ])
