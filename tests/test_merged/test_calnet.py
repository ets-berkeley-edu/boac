from boac.merged import calnet as subject
from boac.models.student import Student
import pytest


@pytest.mark.usefixtures('db_session')
class TestCalnet:
    """TestCalnet"""

    def test_refresh_cohort_attributes(self, app):
        athlete = Student.query.filter_by(uid='61889').first()
        original_sid = athlete.sid
        athlete.uid = None
        athlete.first_name = None
        athlete.last_name = None
        subject.refresh_cohort_attributes(app, [athlete])

        assert athlete.sid == original_sid
        # For this test, assume that there are no blank attributes.
        assert athlete.uid
        assert athlete.first_name == 'Oski'
        assert athlete.last_name == 'Bear'
