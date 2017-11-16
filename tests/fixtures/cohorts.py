from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.team_member import TeamMember
import pytest


@pytest.fixture
def fixture_team_members(db_session):
    field_hockey_star = TeamMember(code='FHW', member_uid='61889', member_csid='11667051', member_name='Brigitte Lin')
    db_session.add(field_hockey_star)
    return [field_hockey_star]


@pytest.fixture
def fixture_custom_cohorts():
    sid = AuthorizedUser.find_by_uid('53791')
    nancy = AuthorizedUser.find_by_uid('95509')
    # Sid gets two custom cohorts
    all_runners = create_cohort(label='Runners', team_codes=['CCM', 'CCW', 'TIM', 'TIW'], uid=sid.uid)
    male_swimmers = create_cohort(label='Swimmers', team_codes=['WPM', 'SDM'], uid=sid.uid)
    # One is shared with Nancy
    CohortFilter.share(male_swimmers.id, nancy.uid)
    return [all_runners, male_swimmers]


def create_cohort(label, team_codes, uid):
    CohortFilter.create(label, team_codes, uid)
    return AuthorizedUser.find_by_uid(uid).cohort_filters[0]
