import boac.models.authorized_user as subject
from boac.models.authorized_user import CohortFilter


class TestAuthorizedUser:
    """Authorized User"""

    def test_load_unknown_user(self, db_session):
        """returns None to Flask-Login for unrecognized UID"""
        unknown_uid = 'Ms. X'
        assert subject.load_user(unknown_uid) is None

    def test_load_admin_user(self, db_session):
        """returns authorization record to Flask-Login for recognized UID"""
        admin_uid = '1133399'
        loaded_user = subject.load_user(admin_uid)
        assert loaded_user.is_active
        assert loaded_user.get_id() == admin_uid
        assert loaded_user.is_admin
        assert len(loaded_user.cohort_filters) > 0

        owners = loaded_user.cohort_filters[0].owners
        assert len(owners) > 0
        assert loaded_user in owners

    def test_create_and_delete_cohort_filter(self, db_session):
        """cohort_filter record to Flask-Login for recognized UID"""
        sebastian_uid = '2040'
        aloysius_uid = '1133399'
        # Create cohort_filter
        cohort_filter = CohortFilter.create(label='High-risk Badminton', team_codes=['MBK', 'WBK'])
        subject.create_cohort_filter(cohort_filter, sebastian_uid)
        sebastian = subject.load_user(sebastian_uid)

        # Share existing cohort_filter
        cohort_filter_id = sebastian.cohort_filters[0].id
        subject.share_cohort_filter(cohort_filter_id, aloysius_uid)
        aloysius = subject.load_user(aloysius_uid)

        owners = sebastian.cohort_filters[0].owners
        assert len(owners) == 2
        assert sebastian, aloysius in owners

        sebastian_count = cohort_filter_count(sebastian_uid)
        aloysius_count = cohort_filter_count(aloysius_uid)

        subject.delete_cohort_filter(cohort_filter_id)
        assert sebastian_count - cohort_filter_count(sebastian_uid) == 1
        assert aloysius_count - cohort_filter_count(aloysius_uid) == 1


def cohort_filter_count(uid):
    return len(subject.load_user(uid).cohort_filters)
