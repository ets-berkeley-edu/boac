"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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


from boac.externals import cal1card_photo_api
from boac.lib.mockingbird import MockResponse, register_mock


class TestCal1CardPhotoApi:
    """Cal1Card Photo API query."""

    def test_get_photo(self, app):
        """Returns fixture data."""
        oski_response = cal1card_photo_api.get_cal1card_photo(61889)
        assert isinstance(oski_response, bytes)
        assert len(oski_response) == 3559

    def test_user_not_found(self, app, caplog):
        """Logs error and returns False when user not found."""
        response = cal1card_photo_api.get_cal1card_photo(9999999)
        assert '404 Client Error' in caplog.text
        assert response is False

    def test_server_error(self, app, caplog):
        """Logs unexpected server errors and returns informative message."""
        api_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(cal1card_photo_api._get_cal1card_photo, api_error):
            response = cal1card_photo_api._get_cal1card_photo(61889)
            assert '500 Server Error' in caplog.text
            assert not response
            assert response.raw_response.status_code == 500
            assert response.raw_response.json()['message']
