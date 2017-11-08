from boac.models.team_member import TeamMember
import pytest


@pytest.fixture
def fixture_cohorts(db_session):
    field_hockey_star = TeamMember(code='FHW', member_uid='61889', member_csid='11667051', member_name='Brigitte Lin')
    db_session.add(field_hockey_star)
    return [field_hockey_star]
