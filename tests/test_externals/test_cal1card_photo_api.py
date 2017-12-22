from boac.externals import cal1card_photo_api
from boac.lib.mockingbird import MockResponse, register_mock


class TestCal1CardPhotoApi:
    """Cal1Card Photo API query"""

    def test_get_photo(self, app):
        """returns fixture data"""
        oski_response = cal1card_photo_api.get_cal1card_photo(61889)
        assert isinstance(oski_response, bytes)
        assert len(oski_response) == 3559

    def test_user_not_found(self, app, caplog):
        """logs error and returns False when user not found"""
        response = cal1card_photo_api.get_cal1card_photo(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert response is False

    def test_server_error(self, app, caplog):
        """logs unexpected server errors and returns informative message"""
        api_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(cal1card_photo_api._get_cal1card_photo, api_error):
            response = cal1card_photo_api._get_cal1card_photo(61889)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response
            assert response.raw_response.status_code == 500
            assert response.raw_response.json()['message']
