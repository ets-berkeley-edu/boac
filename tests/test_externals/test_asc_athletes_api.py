from boac.externals import asc_athletes_api
from boac.lib.mockingbird import MockResponse, register_mock


class TestAscAthletesApi:

    def test_fixture(self, app):
        raw_response = asc_athletes_api._get_current_feed()
        assert raw_response.status_code == 200
        parsed_response = raw_response.json()
        assert parsed_response['1160.4']['SyncDate'] == '2018-01-31'

    def test_get_current_feed(self, app):
        feed = asc_athletes_api.get_current_feed()
        assert len(feed) == 9
        assert feed[0]['SyncDate'] == '2018-01-31'

    def test_sync_date_management(self, app):
        first_date = '2018-01-21'
        assert asc_athletes_api.get_last_sync_date() is None
        asc_athletes_api.confirm_sync(first_date)
        assert asc_athletes_api.get_last_sync_date() == first_date
        last_date = '2018-02-01'
        asc_athletes_api.confirm_sync(last_date)
        assert asc_athletes_api.get_last_sync_date() == last_date


class TestAscAthletesApiUpdates:

    def test_feed_stashing(self, app):
        feed_date = '2018-01-31'
        assert asc_athletes_api.get_past_feed(feed_date) is None
        updates = asc_athletes_api.get_updates()
        assert updates['last_sync_date'] is None
        assert updates['this_sync_date'] == feed_date
        update_feed = updates['feed']
        assert len(update_feed) == 9
        assert update_feed[0]['SyncDate'] == feed_date
        stashed = asc_athletes_api.get_past_feed(feed_date)
        assert len(stashed) == 9
        assert stashed[0]['SyncDate'] == feed_date

    def test_last_sync_date(self, app):
        first_date = '2018-01-21'
        asc_athletes_api.confirm_sync(first_date)
        updates = asc_athletes_api.get_updates()
        assert updates['last_sync_date'] == first_date
        assert updates['this_sync_date'] == '2018-01-31'

    def test_consistency_check(self, app):
        bad_date = '"It\'s not you, it\'s me"'
        with open(app.config['BASE_DIR'] + '/fixtures/asc_athletes.json') as file:
            modified_response_body = file.read().replace('"2018-01-31"', bad_date, 1)
            modified_response = MockResponse(200, {}, modified_response_body)
            with register_mock(asc_athletes_api._get_current_feed, modified_response):
                feed = asc_athletes_api.get_updates()
                assert feed['error']
                assert not feed.get('feed')

    def test_repeat_date_not_stashed(self, app):
        feed_date = '2018-01-31'
        asc_athletes_api.confirm_sync(feed_date)
        asc_athletes_api.get_updates()
        assert asc_athletes_api.get_past_feed(feed_date) is None
