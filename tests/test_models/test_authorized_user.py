from boac.models.authorized_user import AuthorizedUser
import pytest


@pytest.mark.usefixtures('db_session')
class TestAuthorizedUser:
    """Authorized User"""

    def test_load_unknown_user(self):
        """returns None to Flask-Login for unrecognized UID"""
        unknown_uid = 'Ms. X'
        assert AuthorizedUser.find_by_uid(unknown_uid) is None

    def test_load_admin_user(self):
        """returns authorization record to Flask-Login for recognized UID"""
        admin_uid = '1133399'
        loaded_user = AuthorizedUser.find_by_uid(admin_uid)
        assert loaded_user.is_active
        assert loaded_user.get_id() == admin_uid
        assert loaded_user.is_admin
        assert len(loaded_user.cohort_filters) > 0

        owners = loaded_user.cohort_filters[0].owners
        assert len(owners) > 0
        assert loaded_user in owners
