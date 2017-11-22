from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter


class TestCohortFilter:
    """Cohort Filter"""

    def test_no_cohort(self, db_session):
        assert not CohortFilter.find_by_id(99999999)
        assert not CohortFilter.all_owned_by('88888888')

    def test_create_and_delete_cohort(self, db_session):
        """cohort_filter record to Flask-Login for recognized UID"""
        owner = AuthorizedUser.find_by_uid('2040')
        shared_with = AuthorizedUser.find_by_uid('1133399')
        # Check validity of UIDs
        assert owner
        assert shared_with

        # Create and share cohort
        cohort = CohortFilter.create(label='High-risk Badminton', team_codes=['MBK', 'WBK'], uid=owner.uid)
        cohort = CohortFilter.share(cohort['id'], shared_with.uid)
        assert len(cohort['owners']) == 2
        assert owner, shared_with in cohort['owners']

        # Delete cohort and verify
        previous_owner_count = cohort_count(owner)
        previous_shared_count = cohort_count(shared_with)
        CohortFilter.delete(cohort['id'])
        assert cohort_count(owner) == previous_owner_count - 1
        assert cohort_count(shared_with) == previous_shared_count - 1


def cohort_count(user):
    return len(CohortFilter.all_owned_by(user.uid))
