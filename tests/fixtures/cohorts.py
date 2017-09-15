from boac.models.cohort import Cohort
import pytest


@pytest.fixture
def fixture_cohorts(db_session):
    field_hockey_star = Cohort('FHW', '61889', '12345678', 'Brigitte Lin')
    db_session.add(field_hockey_star)
    db_session.commit()
    return [field_hockey_star]
