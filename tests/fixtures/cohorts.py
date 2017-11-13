from boac.models import authorized_user
from boac.models.authorized_user import CohortFilter
from boac.models.team_member import TeamMember
import pytest


@pytest.fixture
def fixture_team_members(db_session):
    field_hockey_star = TeamMember(code='FHW', member_uid='61889', member_csid='11667051', member_name='Brigitte Lin')
    db_session.add(field_hockey_star)
    return [field_hockey_star]


@pytest.fixture
def fixture_custom_cohorts():
    all_runners = CohortFilter.create(label='Runners', team_codes=['CCM', 'CCW', 'TIM', 'TIW'])
    male_swimmers = CohortFilter.create(label='Swimmers', team_codes=['WPM', 'SDM'])
    sid = authorized_user.load_user('53791')
    nancy = authorized_user.load_user('95509')
    # Sid gets two custom cohorts
    all_runners = create_cohort_filter(all_runners, sid.uid)
    male_swimmers = create_cohort_filter(male_swimmers, sid.uid)
    # One is shared with Nancy
    authorized_user.share_cohort_filter(male_swimmers.id, nancy.uid)
    return [all_runners, male_swimmers]


def create_cohort_filter(cohort_filter, user_id):
    authorized_user.create_cohort_filter(cohort_filter, user_id)
    return authorized_user.load_user(user_id=user_id).cohort_filters[0]
