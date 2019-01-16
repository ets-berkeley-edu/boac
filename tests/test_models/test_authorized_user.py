"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


from boac.models.authorized_user import AuthorizedUser
import pytest


@pytest.mark.usefixtures('db_session')
class TestAuthorizedUser:
    """Authorized user."""

    def test_load_unknown_user(self):
        """Returns None to Flask-Login for unrecognized UID."""
        unknown_uid = 'Ms. X'
        assert AuthorizedUser.find_by_uid(unknown_uid) is None

    def test_load_admin_user(self):
        """Returns authorization record to Flask-Login for recognized UID."""
        admin_uid = '2040'
        loaded_user = AuthorizedUser.find_by_uid(admin_uid)
        assert loaded_user.is_active
        assert loaded_user.get_id() == admin_uid
        assert loaded_user.is_admin
        assert len(loaded_user.cohort_filters) > 0

        owners = loaded_user.cohort_filters[0].owners
        assert len(owners) > 0
        assert loaded_user in owners
