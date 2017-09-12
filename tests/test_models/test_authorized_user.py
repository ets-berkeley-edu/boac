import boac.models.authorized_user as subject

class TestAuthorizedUser:
    '''Authorized User'''

    def test_load_unknown_user(self, db_session):
        '''returns None to Flask-Login for unrecognized UID'''
        unknown_uid = 'Ms. X'
        assert subject.load_user(unknown_uid) is None

    def test_load_admin_user(self, db_session):
        '''returns authorization record to Flask-Login for recognized UID'''
        admin_uid = '1133399'
        loaded_user = subject.load_user(admin_uid)
        assert loaded_user.is_active
        assert loaded_user.get_id() == admin_uid
        assert loaded_user.is_admin
