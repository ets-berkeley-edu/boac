from datetime import date
from boac.models.job_progress import JobProgress
import pytest


@pytest.mark.usefixtures('db_session')
class TestJobProgress:
    """Background Job Process Tracker"""

    def test_start_and_end(self):
        assert JobProgress().get() is None
        progress = JobProgress().start()
        assert progress['start'].startswith(str(date.today()))
        assert progress['end'] is None
        progress = JobProgress().end()
        assert progress['end'].startswith(str(date.today()))

    def test_does_not_update_an_unstarted_job(self):
        assert JobProgress().get() is None
        progress = JobProgress().update('False step')
        assert progress is False

    def test_updates_a_started_job(self):
        assert JobProgress().start()
        progress = JobProgress().update('First step')
        assert len(progress['steps']) == 1
        assert progress['steps'][0].startswith(str(date.today()))
        assert progress['steps'][0].endswith('First step')
        progress = JobProgress().update('Next step')
        assert len(progress['steps']) == 2
        assert progress['steps'][1].endswith('Next step')

    def test_does_not_update_an_ended_job(self):
        assert JobProgress().start()
        assert JobProgress().end()
        progress = JobProgress().update('Into the wall')
        assert progress is False

    def test_delete_job(self):
        assert JobProgress().start()
        assert JobProgress().start() is False
        assert JobProgress().delete()
        assert JobProgress().start()
