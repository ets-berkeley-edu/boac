from boac.lib import merged as subject


class TestMerged:
    """TestMerged"""

    def test_refresh_cohort_attributes(self, app, fixture_team_members):
        members = fixture_team_members
        original_csids = (m.member_csid for m in members)
        for member in members:
            member.member_uid = None
            member.member_name = None
        subject.refresh_cohort_attributes_from_calnet(app, members)
        for member in members:
            assert member.member_csid in original_csids
            # For this test, assume that there are no blank attributes.
            assert member.member_uid
            assert member.member_name
