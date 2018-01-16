"""Official access to Cal1Card photos."""

from boac.lib import http
from boac.lib.mockingbird import fixture
from flask import current_app as app
from requests.auth import HTTPBasicAuth


def get_cal1card_photo(uid):
    response = _get_cal1card_photo(uid)
    if response:
        return response.content
    else:
        if hasattr(response, 'raw_response') and hasattr(response.raw_response, 'status_code') and response.raw_response.status_code == 404:
            return False
        else:
            return None


@fixture('cal1card_photo_{uid}.jpg')
def _get_cal1card_photo(uid, mock=None):
    url = http.build_url(app.config['CAL1CARD_PHOTO_API_URL'], {'uid': uid})
    with mock(url):
        return http.request(url, auth=cal1card_api_auth())


def cal1card_api_auth():
    return HTTPBasicAuth(app.config['CAL1CARD_PHOTO_API_USERNAME'], app.config['CAL1CARD_PHOTO_API_PASSWORD'])
