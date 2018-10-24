"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


from boac.lib import http
from boac.lib.mockingbird import fixture
from flask import current_app as app
from requests.auth import HTTPBasicAuth


"""Official access to Cal1Card photos."""


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
