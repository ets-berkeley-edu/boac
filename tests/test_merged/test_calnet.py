from boac.merged import calnet as subject
from boac.models.team_member import TeamMember
import pytest


@pytest.mark.usefixtures('db_session')
class TestCalnet:
    """TestCalnet"""

    def test_refresh_cohort_attributes(self, app):
        athlete = TeamMember.query.filter_by(member_uid='61889').first()
        original_sid = athlete.member_csid
        athlete.member_uid = None
        athlete.first_name = None
        athlete.last_name = None
        subject.refresh_cohort_attributes(app, [athlete])

        assert athlete.member_csid == original_sid
        # For this test, assume that there are no blank attributes.
        assert athlete.member_uid
        assert athlete.first_name == 'Oski'
        assert athlete.last_name == 'Bear'
