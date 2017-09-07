""" This package integrates with Flask-Login to determine who can use the app,
and which privileges they have. It will probably end up as a DB table, but is
simply mocked-out a la "demo mode" for now.
"""

from collections import namedtuple
import csv
from flask_login import UserMixin

MockedUser = namedtuple('MockedUser', 'uid is_admin is_director is_advisor')

class AuthorizedUser(MockedUser, UserMixin):
    def get_id(self):
        """Override UserMixin, since our DB conventionally reserves 'id' for generated keys."""
        return self.uid


_mocked_users_csv = """uid,is_admin,is_director,is_advisor
2040,true,false,false
53791,true,false,false
95509,true,false,false
177473,true,false,false
1133399,true,false,false
211159,true,false,false
242881,true,false,false
1022796,true,false,false
"""
_csv_reader = csv.DictReader(_mocked_users_csv.splitlines())
_mocked_users = {m['uid']: AuthorizedUser(**m) for m in _csv_reader}

def load_user(user_id):
    return _mocked_users.get(user_id)
