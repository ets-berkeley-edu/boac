"""
Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.

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

import pytest
from sqlalchemy import event

from boac import db, std_commit
from boac.lib.util import utc_now
from boac.merged.calnet import get_calnet_user_for_uid
from boac.merged.user_tag import (
    BATCH_NOTE,
    DELETED_USER,
    NO_ACCESS,
    OUTSIDE_PEER_DEPARTMENT,
    PRIVATE_NOTE,
    SELF_TAG,
    TagContext,
    find_invalid_tags,
    get_tagged_uids,
    search_taggable_users,
    writer_peer_department_id,
)
from boac.models.authorized_user import AuthorizedUser
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.university_dept import UniversityDept
from boac.models.university_dept_member import UniversityDeptMember

# Fixture UIDs, described in .claude/docs/permissions.md.
WRITER_UID = '6446'
REGULAR_ADVISOR_UID = '1081940'
CE3_ADVISOR_UID = '5405613'
CE3_NAVCAL_MANAGER_UID = '2525'
EOP_MANAGER_UID = '3535'
EOP_PEER_ADVISOR_UID = '1563405'
NAVCAL_PEER_ADVISOR_UID = '188444'
NO_ADVISING_DATA_UID = '19735'
DELETED_UID = '1015674'
NOT_A_USER_UID = '999999999'


def _give_deleted_user_advisor_role():
    # The fixture's deleted user holds no department role, so add one that would make a live user a tagging candidate.
    deleted_user = AuthorizedUser.find_by_uid('1015674', ignore_deleted=False)
    deleted_user.can_access_advising_data = True
    UniversityDeptMember.create_or_update_membership(UniversityDept.find_by_dept_code('COENG').id, deleted_user.id, role='advisor')
    std_commit()


def _eop_id():
    return PeerAdvisingDepartment.get_department_by_name('Educational Opportunity Program').id


def _name(app, uid):
    # Fixture names are read from the mock CalNet record, never hard-coded in tests.
    return get_calnet_user_for_uid(app, uid)['name']


def _uids(results):
    return [r['uid'] for r in results]


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


@pytest.mark.usefixtures('db_session')
class TestGetTaggedUids:

    def test_get_tagged_uids(self):
        """Only UIDs with an authorized_users row are tags, deleted users included, in body order without duplicates."""
        body = f'<p>@{REGULAR_ADVISOR_UID} @{NOT_A_USER_UID} @{DELETED_UID} @{REGULAR_ADVISOR_UID} @3</p>'
        assert get_tagged_uids(body) == [REGULAR_ADVISOR_UID, DELETED_UID]

    def test_empty_body(self):
        assert get_tagged_uids(None) == []
        assert get_tagged_uids('') == []


@pytest.mark.usefixtures('db_session')
class TestFindInvalidTags:

    def test_regular_advisor(self):
        assert find_invalid_tags([REGULAR_ADVISOR_UID], TagContext(writer_uid=WRITER_UID)) == []

    def test_unknown_uid_is_not_a_tag(self):
        assert find_invalid_tags([NOT_A_USER_UID], TagContext(writer_uid=WRITER_UID)) == []

    def test_deleted_user(self):
        result = find_invalid_tags([DELETED_UID], TagContext(writer_uid=WRITER_UID))
        assert result == [{'uid': DELETED_UID, 'reason': DELETED_USER}]
        assert DELETED_USER == 'deleted_user'

    def test_deleted_user_with_department_role(self):
        """A deleted user is rejected even while they still hold an advisor role with advising data."""
        _give_deleted_user_advisor_role()
        result = find_invalid_tags([DELETED_UID], TagContext(writer_uid=WRITER_UID))
        assert result == [{'uid': DELETED_UID, 'reason': DELETED_USER}]

    def test_deleted_user_reason_wins(self):
        context = TagContext(writer_uid=WRITER_UID, is_private=True, is_batch=True)
        assert find_invalid_tags([DELETED_UID], context) == [{'uid': DELETED_UID, 'reason': DELETED_USER}]

    def test_batch_note(self):
        context = TagContext(writer_uid=WRITER_UID, is_batch=True)
        result = find_invalid_tags([REGULAR_ADVISOR_UID, CE3_ADVISOR_UID], context)
        assert result == [
            {'uid': REGULAR_ADVISOR_UID, 'reason': BATCH_NOTE},
            {'uid': CE3_ADVISOR_UID, 'reason': BATCH_NOTE},
        ]
        assert BATCH_NOTE == 'batch_note'

    def test_private_note_rejects_non_ce3(self):
        context = TagContext(writer_uid=WRITER_UID, is_private=True)
        result = find_invalid_tags([REGULAR_ADVISOR_UID], context)
        assert result == [{'uid': REGULAR_ADVISOR_UID, 'reason': PRIVATE_NOTE}]
        assert PRIVATE_NOTE == 'private_note'

    def test_private_note_allows_ce3(self):
        context = TagContext(writer_uid=WRITER_UID, is_private=True)
        assert find_invalid_tags([CE3_ADVISOR_UID, CE3_NAVCAL_MANAGER_UID], context) == []

    def test_peer_advisor_on_regular_note(self):
        result = find_invalid_tags([EOP_PEER_ADVISOR_UID], TagContext(writer_uid=WRITER_UID))
        assert result == [{'uid': EOP_PEER_ADVISOR_UID, 'reason': NO_ACCESS}]
        assert NO_ACCESS == 'no_access'

    def test_advisor_without_advising_data(self):
        result = find_invalid_tags([NO_ADVISING_DATA_UID], TagContext(writer_uid=WRITER_UID))
        assert result == [{'uid': NO_ADVISING_DATA_UID, 'reason': NO_ACCESS}]

    def test_self_tag_new(self):
        result = find_invalid_tags([WRITER_UID], TagContext(writer_uid=WRITER_UID))
        assert result == [{'uid': WRITER_UID, 'reason': SELF_TAG}]
        assert SELF_TAG == 'self_tag'

    def test_self_tag_existing(self):
        """A self-tag already saved on the note is left alone, so editing an old note never fails on it."""
        assert find_invalid_tags([WRITER_UID], TagContext(writer_uid=WRITER_UID), new_uids=[]) == []

    def test_peer_writer_inside_group(self):
        eop_id = _eop_id()
        context = TagContext(writer_uid=EOP_PEER_ADVISOR_UID, note_peer_department_id=eop_id, writer_peer_department_id=eop_id)
        assert find_invalid_tags([EOP_MANAGER_UID], context) == []

    def test_peer_writer_outside_group(self):
        eop_id = _eop_id()
        context = TagContext(writer_uid=EOP_PEER_ADVISOR_UID, note_peer_department_id=eop_id, writer_peer_department_id=eop_id)
        result = find_invalid_tags([REGULAR_ADVISOR_UID], context)
        assert result == [{'uid': REGULAR_ADVISOR_UID, 'reason': OUTSIDE_PEER_DEPARTMENT}]
        assert OUTSIDE_PEER_DEPARTMENT == 'outside_peer_department'

    def test_peer_writer_other_groups_peer(self):
        """A peer advisor from another group cannot read the note, so no_access outranks outside_peer_department."""
        eop_id = _eop_id()
        context = TagContext(writer_uid=EOP_PEER_ADVISOR_UID, note_peer_department_id=eop_id, writer_peer_department_id=eop_id)
        result = find_invalid_tags([NAVCAL_PEER_ADVISOR_UID], context)
        assert result == [{'uid': NAVCAL_PEER_ADVISOR_UID, 'reason': NO_ACCESS}]

    def test_peer_writer_existing_tag_not_rechecked(self):
        eop_id = _eop_id()
        context = TagContext(writer_uid=EOP_PEER_ADVISOR_UID, note_peer_department_id=eop_id, writer_peer_department_id=eop_id)
        assert find_invalid_tags([REGULAR_ADVISOR_UID], context, new_uids=[]) == []

    def test_manager_tags_own_group_peer_advisor(self):
        """A manager's context has no writer_peer_department_id, so the outside-department rule never applies to them."""
        context = TagContext(writer_uid=EOP_MANAGER_UID, note_peer_department_id=_eop_id())
        assert find_invalid_tags([EOP_PEER_ADVISOR_UID], context) == []

    def test_order_and_first_reason(self):
        context = TagContext(writer_uid=WRITER_UID, is_private=True)
        result = find_invalid_tags([DELETED_UID, REGULAR_ADVISOR_UID], context)
        assert result == [
            {'uid': DELETED_UID, 'reason': DELETED_USER},
            {'uid': REGULAR_ADVISOR_UID, 'reason': PRIVATE_NOTE},
        ]

    def test_disabled_user_is_taggable(self):
        """Disabling a user blocks login, not tagging."""
        AuthorizedUser.find_by_uid(REGULAR_ADVISOR_UID).disabled_at = utc_now()
        std_commit()
        assert find_invalid_tags([REGULAR_ADVISOR_UID], TagContext(writer_uid=WRITER_UID)) == []


@pytest.mark.usefixtures('db_session')
class TestSearchTaggableUsers:

    def test_blank_snippet(self):
        context = TagContext(writer_uid=WRITER_UID)
        assert search_taggable_users('   ', context) == []
        assert search_taggable_users(None, context) == []

    def test_batch_note(self, app):
        context = TagContext(writer_uid=WRITER_UID, is_batch=True)
        assert search_taggable_users(_name(app, REGULAR_ADVISOR_UID), context) == []

    def test_finds_by_mid_name_substring_any_case(self, app):
        """Odd case and padding in the snippet match the same people as the trimmed lowercase form."""
        context = TagContext(writer_uid=WRITER_UID)
        name = _name(app, REGULAR_ADVISOR_UID)
        lower = search_taggable_users(name.lower(), context)
        padded = search_taggable_users(f'  {name.upper()}  ', context)
        assert REGULAR_ADVISOR_UID in _uids(lower)
        assert REGULAR_ADVISOR_UID in _uids(padded)
        assert lower == padded
        # A snippet taken from the middle of the name matches too.
        assert REGULAR_ADVISOR_UID in _uids(search_taggable_users(name[1:-1], context))

    def test_search_is_one_query_when_names_are_cached(self, app):
        """The people search runs on every pause in typing, and each query is a network round trip, so a warm search is one."""
        context = TagContext(writer_uid=WRITER_UID)
        name = _name(app, REGULAR_ADVISOR_UID)
        # The first search may fetch names CalNet hasn't cached yet; the second finds them all in the cache.
        search_taggable_users(name, context)
        with _count_queries() as statements:
            results = search_taggable_users(name, context)
        assert REGULAR_ADVISOR_UID in _uids(results)
        assert len(statements) == 1

    def test_non_matching_names_are_filtered_in_the_database(self):
        """A snippet matching nobody returns an empty list, whichever way the match is decided."""
        context = TagContext(writer_uid=WRITER_UID)
        assert search_taggable_users('zzzzqqqq', context) == []

    def test_snippet_with_like_wildcards_is_literal(self):
        """A percent sign or underscore in the snippet matches itself, never everyone."""
        context = TagContext(writer_uid=WRITER_UID)
        assert search_taggable_users('%', context) == []
        assert search_taggable_users('_', context) == []

    def test_result_shape_and_limit(self):
        context = TagContext(writer_uid=WRITER_UID)
        results = search_taggable_users('a', context)
        # An empty list would satisfy every check below, so require matches.
        assert results
        assert len(results) <= 8
        for result in results:
            assert set(result.keys()) == {'uid', 'name', 'title', 'deptName'}
        names = [r['name'] for r in results]
        assert names == sorted(names, key=str.casefold)
        # Whatever the search suggests must pass the save-time rules.
        for result in results:
            assert find_invalid_tags([result['uid']], context) == []

    def test_excludes_writer_deleted_and_no_access(self, app):
        context = TagContext(writer_uid=WRITER_UID)
        for uid in [WRITER_UID, DELETED_UID, NO_ADVISING_DATA_UID, EOP_PEER_ADVISOR_UID]:
            assert uid not in _uids(search_taggable_users(_name(app, uid), context))

    def test_excludes_deleted_user_with_department_role(self, app):
        """The search leaves out a deleted user who still holds an advisor role with advising data."""
        _give_deleted_user_advisor_role()
        context = TagContext(writer_uid=WRITER_UID)
        assert DELETED_UID not in _uids(search_taggable_users(_name(app, DELETED_UID), context))

    def test_private_note_finds_only_ce3(self, app):
        context = TagContext(writer_uid=WRITER_UID, is_private=True)
        assert CE3_ADVISOR_UID in _uids(search_taggable_users(_name(app, CE3_ADVISOR_UID), context))
        assert REGULAR_ADVISOR_UID not in _uids(search_taggable_users(_name(app, REGULAR_ADVISOR_UID), context))

    def test_peer_writer_finds_only_own_group(self, app):
        eop_id = _eop_id()
        context = TagContext(writer_uid=EOP_PEER_ADVISOR_UID, note_peer_department_id=eop_id, writer_peer_department_id=eop_id)
        assert EOP_MANAGER_UID in _uids(search_taggable_users(_name(app, EOP_MANAGER_UID), context))
        assert REGULAR_ADVISOR_UID not in _uids(search_taggable_users(_name(app, REGULAR_ADVISOR_UID), context))
        assert NAVCAL_PEER_ADVISOR_UID not in _uids(search_taggable_users(_name(app, NAVCAL_PEER_ADVISOR_UID), context))

    def test_disabled_user_found(self, app):
        """Disabling a user blocks login, not tagging, so the search still suggests them."""
        AuthorizedUser.find_by_uid(REGULAR_ADVISOR_UID).disabled_at = utc_now()
        std_commit()
        context = TagContext(writer_uid=WRITER_UID)
        assert REGULAR_ADVISOR_UID in _uids(search_taggable_users(_name(app, REGULAR_ADVISOR_UID), context))


@pytest.mark.usefixtures('db_session')
class TestWriterPeerDepartmentId:
    """Who the outside-peer-department rule limits."""

    def test_peer_advisor_gets_department(self):
        """A peer advisor writing in their own group is limited to that group."""
        user_id = AuthorizedUser.get_id_per_uid(EOP_PEER_ADVISOR_UID)
        assert writer_peer_department_id(user_id, _eop_id()) == _eop_id()

    def test_manager_is_not_limited(self):
        """A peer advisor manager is staff, so the rule doesn't limit them."""
        user_id = AuthorizedUser.get_id_per_uid(EOP_MANAGER_UID)
        assert writer_peer_department_id(user_id, _eop_id()) is None

    def test_non_member_is_not_limited(self):
        """A regular advisor has no peer membership to limit them."""
        user_id = AuthorizedUser.get_id_per_uid(WRITER_UID)
        assert writer_peer_department_id(user_id, _eop_id()) is None

    def test_other_group(self):
        """A peer advisor in another group gets no department for this one."""
        user_id = AuthorizedUser.get_id_per_uid(NAVCAL_PEER_ADVISOR_UID)
        assert writer_peer_department_id(user_id, _eop_id()) is None

    def test_no_department(self):
        """A note with no peer department never limits the writer."""
        user_id = AuthorizedUser.get_id_per_uid(EOP_PEER_ADVISOR_UID)
        assert writer_peer_department_id(user_id, None) is None

    def test_soft_deleted_membership(self):
        """A soft-deleted membership no longer makes the writer a peer advisor of that group."""
        user_id = AuthorizedUser.get_id_per_uid(EOP_PEER_ADVISOR_UID)
        membership = PeerAdvisingDepartmentMember.query.filter_by(
            authorized_user_id=user_id,
            peer_advising_department_id=_eop_id(),
        ).first()
        membership.deleted_at = utc_now()
        std_commit()
        assert writer_peer_department_id(user_id, _eop_id()) is None
