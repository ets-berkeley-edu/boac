from boac.models.cohort import Cohort
import pytest


@pytest.fixture
def fixture_cohorts(db_session):
    field_hockey_star = Cohort('FHW', '61889', '11667051', 'Brigitte Lin')
    db_session.add(field_hockey_star)
    db_session.commit()
    return [field_hockey_star]
