from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter


class TestCohortFilter:
    """Cohort Filter"""

    def test_create_and_delete_cohort(self, db_session):
        """cohort_filter record to Flask-Login for recognized UID"""
        sebastian_uid = '2040'
        aloysius_uid = '1133399'
        # Create cohort_filter
        CohortFilter.create(label='High-risk Badminton', team_codes=['MBK', 'WBK'], uid=sebastian_uid)
        sebastian = AuthorizedUser.find_by_uid(sebastian_uid)

        # Share existing cohort_filter
        cohort_filter_id = sebastian.cohort_filters[0].id
        CohortFilter.share(cohort_filter_id, aloysius_uid)
        aloysius = AuthorizedUser.find_by_uid(aloysius_uid)

        owners = sebastian.cohort_filters[0].owners
        assert len(owners) == 2
        assert sebastian, aloysius in owners

        sebastian_count = cohort_filter_count(sebastian_uid)
        aloysius_count = cohort_filter_count(aloysius_uid)

        CohortFilter.delete(cohort_filter_id)
        assert sebastian_count - cohort_filter_count(sebastian_uid) == 1
        assert aloysius_count - cohort_filter_count(aloysius_uid) == 1


def cohort_filter_count(uid):
    return len(AuthorizedUser.find_by_uid(uid).cohort_filters)
