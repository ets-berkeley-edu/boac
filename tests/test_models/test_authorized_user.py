"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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

from datetime import datetime

from boac.models.authorized_user import AuthorizedUser
import pytest

unknown_uid = 'Ms. X'
admin_uid = '2040'
coe_advisor_uid = '1133399'


@pytest.mark.usefixtures('db_session')
class TestAuthorizedUser:
    """Authorized user."""

    def test_load_unknown_user(self):
        """Returns None to Flask-Login for unrecognized UID."""
        assert AuthorizedUser.find_by_uid(unknown_uid) is None

    def test_load_admin_user(self, admin_user_uid):
        """Returns authorization record to Flask-Login for recognized UID."""
        loaded_user = AuthorizedUser.find_by_uid(admin_user_uid)
        assert loaded_user.uid == admin_user_uid
        assert loaded_user.is_admin
        assert len(loaded_user.cohort_filters) > 0
        assert loaded_user.cohort_filters[0].owner == loaded_user

    def test_create_or_restore_deleted(self):
        """Restores a deleted user to a non-deleted state, updating with any passed-in attributes."""
        user = AuthorizedUser.find_by_uid(uid=coe_advisor_uid)
        user.created_by = '0'
        user.deleted_at = datetime.now()
        assert user.can_access_advising_data is True
        assert user.can_access_canvas_data is True

        restored_user = AuthorizedUser.create_or_restore(
            coe_advisor_uid,
            created_by=admin_uid,
            can_access_advising_data=False,
            can_access_canvas_data=False,
        )
        assert restored_user.can_access_advising_data is False
        assert restored_user.can_access_canvas_data is False
        assert restored_user.created_by == admin_uid
        assert restored_user.deleted_at is None

    def test_create_or_restore_existing(self):
        """Updates an existing user, replacing existing attributes that are False with any attributes passed in as True."""
        user = AuthorizedUser.find_by_uid(uid=admin_uid)
        user.can_access_advising_data = False
        user.can_access_canvas_data = False
        user.created_by = admin_uid

        updated_user = AuthorizedUser.create_or_restore(
            admin_uid,
            created_by='0',
            is_admin=False,
            can_access_advising_data=True,
            can_access_canvas_data=True,
        )
        assert updated_user.is_admin is True
        assert updated_user.can_access_advising_data is True
        assert updated_user.can_access_canvas_data is True
        assert updated_user.created_by == '0'

    def test_create_or_restore_new(self):
        """Creates a new user if it doesn't already exist."""
        new_user = AuthorizedUser.create_or_restore(
            unknown_uid,
            created_by='0',
            is_admin=False,
            can_access_advising_data=True,
            can_access_canvas_data=False,
        )
        assert new_user.is_admin is False
        assert new_user.can_access_advising_data is True
        assert new_user.can_access_canvas_data is False
        assert new_user.in_demo_mode is False
        assert new_user.created_by == '0'

    def test_create_or_restore_blocked(self):
        """Does not restore a user if they have been blocked."""
        blocked_user = AuthorizedUser.find_by_uid(uid=coe_advisor_uid)
        blocked_user.is_blocked = True

        assert not AuthorizedUser.create_or_restore(coe_advisor_uid, created_by='0')
