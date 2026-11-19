"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from contextlib import contextmanager
from datetime import datetime

import pytest
from sqlalchemy import event

from boac import db, std_commit
from boac.lib.util import utc_now
from boac.models.authorized_user import AuthorizedUser
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.university_dept import UniversityDept
from boac.models.university_dept_member import UniversityDeptMember

admin_uid = '177473'
coe_advisor_uid = '1133399'
unknown_uid = 'Ms. X'


@pytest.mark.usefixtures('db_session')
class TestAuthorizedUser:
    """Authorized user."""

    def test_load_unknown_user(self):
        """Returns None to Flask-Login for unrecognized UID."""
        assert AuthorizedUser.find_by_uid(unknown_uid) is None

    def test_load_admin_user(self):
        """Returns authorization record to Flask-Login for recognized UID."""
        loaded_user = AuthorizedUser.find_by_uid(admin_uid)
        assert loaded_user.uid == admin_uid
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


@contextmanager
def _count_queries():
    """Collect every SQL statement the engine executes inside the block."""
    statements = []

    def _on_execute(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(db.engine, 'before_cursor_execute', _on_execute)
    try:
        yield statements
    finally:
        event.remove(db.engine, 'before_cursor_execute', _on_execute)


def _candidate_uids(snippet, peer_department_ids=()):
    return [c['uid'] for c in AuthorizedUser.get_tag_candidates(snippet, peer_department_ids)]


def _give_deleted_user_advisor_role():
    # The fixture's deleted user holds no department role, so add one that would make a live user a tagging candidate.
    deleted_user = AuthorizedUser.find_by_uid('1015674', ignore_deleted=False)
    deleted_user.can_access_advising_data = True
    UniversityDeptMember.create_or_update_membership(UniversityDept.find_by_dept_code('COENG').id, deleted_user.id, role='advisor')
    std_commit()


def _eop_id():
    return PeerAdvisingDepartment.get_department_by_name('Educational Opportunity Program').id


def _navcal_id():
    return PeerAdvisingDepartment.get_department_by_name('NAVCAL').id


@pytest.mark.usefixtures('db_session')
class TestTagLookups:
    """Single-query lookups that back @-tagging of users in notes."""

    def test_existing_uids(self):
        """Returns the UIDs that have a row, deleted users included, and skips the query for empty input."""
        assert AuthorizedUser.get_existing_uids(['1081940', '1015674', '999999999']) == {'1081940', '1015674'}
        with _count_queries() as statements:
            assert AuthorizedUser.get_existing_uids([]) == set()
        assert len(statements) == 0

    def test_integer_uids_behave_like_strings(self):
        """A UID sent as a JSON number is looked up as its string form instead of raising a database error."""
        assert AuthorizedUser.get_existing_uids([1081940]) == {'1081940'}
        assert '1081940' in AuthorizedUser.get_tag_eligibility([1081940])

    def test_eligibility_flags(self):
        """Reports CE3, role, access, deletion and peer-department flags per UID."""
        eligibility = AuthorizedUser.get_tag_eligibility(['5405613', '1081940', '1563405', '2525', '1015674', '999999999'])
        assert '999999999' not in eligibility

        ce3 = eligibility['5405613']
        assert ce3['is_ce3'] is True
        assert ce3['is_advisor_or_director'] is True
        assert ce3['can_access_advising_data'] is True

        non_ce3 = eligibility['1081940']
        assert non_ce3['is_ce3'] is False
        assert non_ce3['is_advisor_or_director'] is True

        peer_advisor = eligibility['1563405']
        assert peer_advisor['is_advisor_or_director'] is False
        assert peer_advisor['can_access_advising_data'] is False
        assert peer_advisor['peer_department_ids'] == {_eop_id()}

        peer_manager = eligibility['2525']
        assert peer_manager['peer_department_ids'] == {_navcal_id()}
        assert peer_manager['is_ce3'] is True

        assert eligibility['1015674']['is_deleted'] is True
        assert eligibility['1081940']['is_deleted'] is False
        assert isinstance(eligibility['1081940']['id'], int)

    def test_eligibility_is_one_query(self):
        """Looks up many UIDs in a single query, and none at all for empty input."""
        uids = ['5405613', '1081940', '1563405', '2525', '1015674', '999999999']
        with _count_queries() as statements:
            AuthorizedUser.get_tag_eligibility(uids)
        assert len(statements) == 1
        with _count_queries() as statements:
            assert AuthorizedUser.get_tag_eligibility([]) == {}
        assert len(statements) == 0

    def test_soft_deleted_peer_membership_is_ignored(self):
        """A soft-deleted peer membership grants nothing."""
        eop_id = _eop_id()
        user_id = AuthorizedUser.get_id_per_uid('1563405')
        membership = PeerAdvisingDepartmentMember.query.filter_by(authorized_user_id=user_id, peer_advising_department_id=eop_id).first()
        membership.deleted_at = utc_now()
        std_commit()
        assert AuthorizedUser.get_tag_eligibility(['1563405'])['1563405']['peer_department_ids'] == set()
        assert '1563405' not in _candidate_uids('', [eop_id])

    def test_deleted_user_with_department_role_is_not_a_candidate(self):
        """A soft-deleted user who still holds an advisor role with advising data is left out of the pool."""
        _give_deleted_user_advisor_role()
        assert '1015674' not in _candidate_uids('')

    def test_candidate_pool(self):
        """Includes advisors and directors with advising data, plus members of the given peer departments."""
        eop_id = _eop_id()
        with _count_queries() as statements:
            uids = _candidate_uids('')
        assert len(statements) == 1
        assert '1081940' in uids
        assert '5405613' in uids
        assert '1563405' not in uids
        assert '19735' not in uids
        assert '1015674' not in uids
        assert uids == sorted(set(uids))

        with _count_queries() as statements:
            uids = _candidate_uids('', [eop_id])
        assert len(statements) == 1
        assert '1563405' in uids
        assert '3535' in uids
        assert '1015674' not in uids
