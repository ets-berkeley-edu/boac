from boac.lib import merged as subject
from boac.models.team_member import TeamMember
import pytest


@pytest.mark.usefixtures('db_session')
class TestMerged:
    """TestMerged"""

    def test_refresh_cohort_attributes(self, app):
        athlete = TeamMember.query.filter_by(member_uid='61889').first()
        original_sid = athlete.member_csid
        athlete.member_uid = None
        athlete.member_name = None
        subject.refresh_cohort_attributes_from_calnet(app, [athlete])

        assert athlete.member_csid == original_sid
        # For this test, assume that there are no blank attributes.
        assert athlete.member_uid
        assert athlete.member_name
