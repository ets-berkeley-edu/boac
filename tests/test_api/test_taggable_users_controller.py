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

import json

import pytest

from boac.merged.calnet import get_calnet_user_for_uid
from boac.models.note import Note
from boac.models.peer_advising_department import PeerAdvisingDepartment
from tests.util import override_config

# Fixture UIDs, described in .claude/docs/permissions.md.
director_uid = '6446'
advisor_uid = '1081940'
ce3_advisor_uid = '5405613'
eop_manager_uid = '3535'
eop_peer_advisor_uid = '1563405'
navcal_peer_advisor_uid = '188444'
no_advising_data_advisor_uid = '1022796'
student_sid = '11667051'


def _eop_id():
    return PeerAdvisingDepartment.get_department_by_name('Educational Opportunity Program').id


def _create_note(author_uid, author_dept_codes=('UWASC',), is_private=False, peer_advising_department_id=None):
    # Synthetic note text only; tagging tests care about who wrote the note and where it lives.
    return Note.create(
        author_uid=author_uid,
        author_name='Synthetic Author',
        author_role='Advisor',
        author_dept_codes=list(author_dept_codes),
        sid=student_sid,
        subject='Synthetic subject',
        body='Synthetic body',
        is_private=is_private,
        peer_advising_department_id=peer_advising_department_id,
    )


def _name(app, uid):
    # Fixture names are read from the mock CalNet record, never hard-coded in tests.
    return get_calnet_user_for_uid(app, uid)['name']


def _uids(results):
    return [r['uid'] for r in results]


def _api_taggable(client, params, expected_status_code=200, headers=None):
    response = client.post(
        '/api/users/taggable',
        data=json.dumps(params),
        content_type='application/json',
        headers=headers or {},
    )
    assert response.status_code == expected_status_code
    return response.json


@pytest.mark.usefixtures('db_session')
class TestFindTaggableUsersAccess:
    """Access checks and context validation for the taggable-users endpoint."""

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        _api_taggable(client, {'snippet': 'a', 'noteId': 1}, expected_status_code=401)

    def test_api_key_without_login(self, app, client):
        """Denies an API key without a login, since a tag search always runs as a person."""
        with override_config(app, 'API_KEY', 'synthetic-key'):
            _api_taggable(
                client,
                {'snippet': 'a', 'peerAdvisingDepartmentId': _eop_id()},
                expected_status_code=401,
                headers={'App-Key': 'synthetic-key'},
            )

    def test_no_locator(self, client, fake_auth):
        """Requires a tag context."""
        fake_auth.login(director_uid)
        _api_taggable(client, {'snippet': 'a'}, expected_status_code=400)

    def test_two_locators(self, client, fake_auth):
        """Rejects more than one tag context."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        _api_taggable(client, {'snippet': 'a', 'noteId': note.id, 'parentNoteId': note.id}, expected_status_code=400)

    def test_half_comment_pair(self, client, fake_auth):
        """A comment context needs both its parent type and id."""
        fake_auth.login(director_uid)
        _api_taggable(client, {'snippet': 'a', 'commentParentType': 'appointment'}, expected_status_code=400)

    def test_bad_comment_type(self, client, fake_auth):
        """Rejects an unknown comment parent type."""
        fake_auth.login(director_uid)
        _api_taggable(client, {'snippet': 'a', 'commentParentType': 'bogus', 'commentParentId': '123'}, expected_status_code=400)

    def test_malformed_ids(self, client, fake_auth):
        """A malformed id or recipient count is a bad request, not a server error."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        _api_taggable(client, {'snippet': 'a', 'noteId': 'abc'}, expected_status_code=400)
        _api_taggable(client, {'snippet': 'a', 'noteId': note.id, 'recipientCount': 'x'}, expected_status_code=400)

    def test_non_object_body(self, client, fake_auth):
        """A JSON body that isn't an object is a bad request, not a server error."""
        fake_auth.login(director_uid)
        for body in ([1, 2], 'abc', 5, True):
            response = client.post('/api/users/taggable', data=json.dumps(body), content_type='application/json')
            assert response.status_code == 400

    def test_non_ascii_digit_id(self, client, fake_auth):
        """A digit-like character that isn't a plain digit is a bad request, not a server error."""
        fake_auth.login(director_uid)
        _api_taggable(client, {'snippet': 'a', 'noteId': '\u00b2'}, expected_status_code=400)

    def test_missing_note(self, client, fake_auth):
        """Returns 404 for a note that doesn't exist."""
        fake_auth.login(director_uid)
        _api_taggable(client, {'snippet': 'a', 'noteId': 999999999}, expected_status_code=404)

    def test_other_authors_note(self, client, fake_auth):
        """Answers a note the caller can't edit exactly like a missing one, so note ids can't be probed."""
        note = _create_note(director_uid)
        fake_auth.login(advisor_uid)
        _api_taggable(client, {'snippet': 'a', 'noteId': note.id}, expected_status_code=404)

    def test_non_member_peer_department(self, client, fake_auth):
        """Denies a new peer note context to someone outside that peer department."""
        fake_auth.login(director_uid)
        _api_taggable(client, {'snippet': 'a', 'peerAdvisingDepartmentId': _eop_id()}, expected_status_code=403)

    def test_unreadable_parent_note(self, client, fake_auth):
        """Hides a parent note the caller can't read."""
        note = _create_note(eop_peer_advisor_uid, author_dept_codes=('ZCEEE',), peer_advising_department_id=_eop_id())
        fake_auth.login(navcal_peer_advisor_uid)
        _api_taggable(client, {'snippet': 'a', 'parentNoteId': note.id}, expected_status_code=404)

    def test_comment_without_advising_data(self, client, fake_auth):
        """Denies an appointment or eForm comment context to someone without advising-data access."""
        fake_auth.login(no_advising_data_advisor_uid)
        _api_taggable(client, {'snippet': 'a', 'commentParentType': 'appointment', 'commentParentId': '123'}, expected_status_code=403)

    def test_own_note_ok(self, client, fake_auth):
        """The author of a note may search for people to tag on it."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        assert isinstance(_api_taggable(client, {'snippet': 'a', 'noteId': note.id}), list)


@pytest.mark.usefixtures('db_session')
class TestFindTaggableUsersResults:
    """Who the taggable-users endpoint suggests for each tag context."""

    def test_finds_colleague_not_self(self, app, client, fake_auth):
        """Suggests a colleague and never the writer."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        assert advisor_uid in _uids(_api_taggable(client, {'snippet': _name(app, advisor_uid), 'noteId': note.id}))
        assert director_uid not in _uids(_api_taggable(client, {'snippet': _name(app, director_uid), 'noteId': note.id}))

    def test_private_ce3_only(self, app, client, fake_auth):
        """On a private note, only CE3 advisors and directors are suggested."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        params = {'noteId': note.id, 'isPrivate': True}
        assert ce3_advisor_uid in _uids(_api_taggable(client, {**params, 'snippet': _name(app, ce3_advisor_uid)}))
        assert advisor_uid not in _uids(_api_taggable(client, {**params, 'snippet': _name(app, advisor_uid)}))

    def test_batch(self, app, client, fake_auth):
        """A note going to more than one student can't carry tags, so no one is suggested."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        assert _api_taggable(client, {'snippet': _name(app, advisor_uid), 'noteId': note.id, 'recipientCount': 2}) == []

    def test_peer_advisor_own_group_only(self, app, client, fake_auth):
        """A peer advisor is offered only members of their own peer advising group."""
        fake_auth.login(eop_peer_advisor_uid)
        params = {'peerAdvisingDepartmentId': _eop_id()}
        assert eop_manager_uid in _uids(_api_taggable(client, {**params, 'snippet': _name(app, eop_manager_uid)}))
        assert advisor_uid not in _uids(_api_taggable(client, {**params, 'snippet': _name(app, advisor_uid)}))

    def test_peer_manager_not_limited(self, app, client, fake_auth):
        """A peer advisor manager is staff, so the peer-group limit doesn't apply."""
        fake_auth.login(eop_manager_uid)
        params = {'peerAdvisingDepartmentId': _eop_id(), 'snippet': _name(app, advisor_uid)}
        assert advisor_uid in _uids(_api_taggable(client, params))

    def test_private_parent_ignores_client_privacy(self, app, client, fake_auth):
        """A comment on a private note is limited to CE3 even when the client says the note isn't private."""
        parent = _create_note(ce3_advisor_uid, author_dept_codes=('ZCEEE',), is_private=True)
        fake_auth.login(eop_manager_uid)
        params = {'parentNoteId': parent.id, 'isPrivate': False, 'snippet': _name(app, advisor_uid)}
        assert advisor_uid not in _uids(_api_taggable(client, params))

    def test_note_comment_by_id_uses_parent_privacy(self, app, client, fake_auth):
        """A note comment passed as noteId takes privacy from its parent, so the client can't widen a private thread."""
        parent = _create_note(ce3_advisor_uid, author_dept_codes=('ZCEEE',), is_private=True)
        comment = Note.create(
            author_uid=ce3_advisor_uid,
            author_name='Synthetic Author',
            author_role='Advisor',
            author_dept_codes=['ZCEEE'],
            sid=student_sid,
            subject='Synthetic subject',
            body='Synthetic comment',
            parent_note_id=parent.id,
        )
        fake_auth.login(ce3_advisor_uid)
        params = {'noteId': comment.id, 'isPrivate': False, 'snippet': _name(app, advisor_uid)}
        assert advisor_uid not in _uids(_api_taggable(client, params))

    def test_comment_context(self, app, client, fake_auth):
        """An appointment comment context accepts a numeric parent id and suggests colleagues."""
        fake_auth.login(director_uid)
        params = {'commentParentType': 'appointment', 'commentParentId': 123, 'snippet': _name(app, advisor_uid)}
        assert advisor_uid in _uids(_api_taggable(client, params))

    def test_snippet_bounds(self, client, fake_auth):
        """An oversized snippet is truncated and a non-string snippet returns no one, without errors."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        _api_taggable(client, {'snippet': 'x' * 500, 'noteId': note.id})
        assert _api_taggable(client, {'snippet': 5, 'noteId': note.id}) == []

    def test_result_shape(self, client, fake_auth):
        """Returns at most 8 people, each with uid, name, title, and department name."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        results = _api_taggable(client, {'snippet': 'a', 'noteId': note.id})
        assert 0 < len(results) <= 8
        for result in results:
            assert set(result.keys()) == {'uid', 'name', 'title', 'deptName'}


deleted_uid = '1015674'


def _api_validate(client, params, expected_status_code=200, headers=None):
    response = client.post(
        '/api/users/tags/validate',
        data=json.dumps(params),
        content_type='application/json',
        headers=headers or {},
    )
    assert response.status_code == expected_status_code
    return response.json


@pytest.mark.usefixtures('db_session')
class TestValidateUserTagsAccess:
    """Access checks and input validation for the tag-validation endpoint, which shares its context checks with autocomplete."""

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        _api_validate(client, {'uids': [advisor_uid], 'noteId': 1}, expected_status_code=401)

    def test_api_key_without_login(self, app, client):
        """Denies an API key without a login, since tags are always checked for a person."""
        with override_config(app, 'API_KEY', 'synthetic-key'):
            _api_validate(
                client,
                {'uids': [advisor_uid], 'peerAdvisingDepartmentId': _eop_id()},
                expected_status_code=401,
                headers={'App-Key': 'synthetic-key'},
            )

    def test_no_locator(self, client, fake_auth):
        """Requires a tag context."""
        fake_auth.login(director_uid)
        _api_validate(client, {'uids': [advisor_uid]}, expected_status_code=400)

    def test_other_authors_note(self, client, fake_auth):
        """Answers a note the caller can't edit exactly like a missing one."""
        note = _create_note(director_uid)
        fake_auth.login(advisor_uid)
        _api_validate(client, {'uids': [ce3_advisor_uid], 'noteId': note.id}, expected_status_code=404)
        _api_validate(client, {'uids': [ce3_advisor_uid], 'noteId': 999999999}, expected_status_code=404)

    def test_non_member_peer_department(self, client, fake_auth):
        """Denies a peer department context to someone outside that department."""
        fake_auth.login(director_uid)
        _api_validate(client, {'uids': [advisor_uid], 'peerAdvisingDepartmentId': _eop_id()}, expected_status_code=403)

    def test_comment_without_advising_data(self, client, fake_auth):
        """Denies an appointment or eForm comment context to someone without advising-data access."""
        fake_auth.login(no_advising_data_advisor_uid)
        params = {'uids': [advisor_uid], 'commentParentType': 'appointment', 'commentParentId': '123'}
        _api_validate(client, params, expected_status_code=403)

    def test_non_object_body(self, client, fake_auth):
        """A JSON body that isn't an object is a bad request, not a server error."""
        fake_auth.login(director_uid)
        for body in ([1, 2], 'abc', 5, True):
            response = client.post('/api/users/tags/validate', data=json.dumps(body), content_type='application/json')
            assert response.status_code == 400

    def test_bad_uids(self, client, fake_auth):
        """Requires uids to be a list of plain digit strings or ints, of bounded length."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        for uids in (None, advisor_uid, {'uid': advisor_uid}, ['abc'], [True], [1.5], [None], [['1']], ['²'], ['-1'], ['1'] * 201):
            params = {'noteId': note.id} if uids is None else {'uids': uids, 'noteId': note.id}
            _api_validate(client, params, expected_status_code=400)


@pytest.mark.usefixtures('db_session')
class TestValidateUserTagsResults:
    """Which tags the tag-validation endpoint reports, and why."""

    def test_all_valid(self, client, fake_auth):
        """A list where everyone may be tagged returns no invalid tags."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        assert _api_validate(client, {'uids': [advisor_uid, ce3_advisor_uid], 'noteId': note.id}) == []

    def test_empty_list(self, client, fake_auth):
        """An empty list returns no invalid tags."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        assert _api_validate(client, {'uids': [], 'noteId': note.id}) == []

    def test_deleted_user(self, app, client, fake_auth):
        """A deleted user is reported as deleted_user, with their name."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        assert _api_validate(client, {'uids': [deleted_uid], 'noteId': note.id}) == [
            {'uid': deleted_uid, 'name': _name(app, deleted_uid), 'reason': 'deleted_user'},
        ]

    def test_private_note(self, app, client, fake_auth):
        """On a private context, a non-CE3 advisor is reported as private_note and a CE3 advisor passes."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        params = {'uids': [advisor_uid, ce3_advisor_uid], 'noteId': note.id, 'isPrivate': True}
        assert _api_validate(client, params) == [{'uid': advisor_uid, 'name': _name(app, advisor_uid), 'reason': 'private_note'}]

    def test_batch(self, client, fake_auth):
        """A note going to more than one student can't carry any tag."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        results = _api_validate(client, {'uids': [advisor_uid], 'noteId': note.id, 'recipientCount': 2})
        assert [r['reason'] for r in results] == ['batch_note']

    def test_no_access(self, client, fake_auth):
        """Someone who can't read the note is reported as no_access."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        results = _api_validate(client, {'uids': [no_advising_data_advisor_uid], 'noteId': note.id})
        assert [r['reason'] for r in results] == ['no_access']

    def test_self_tag(self, client, fake_auth):
        """Every UID counts as newly added, so tagging yourself is reported."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        results = _api_validate(client, {'uids': [director_uid], 'noteId': note.id})
        assert [r['reason'] for r in results] == ['self_tag']

    def test_outside_peer_department(self, client, fake_auth):
        """A peer advisor tagging someone outside their peer department is reported."""
        fake_auth.login(eop_peer_advisor_uid)
        params = {'uids': [eop_manager_uid, advisor_uid], 'peerAdvisingDepartmentId': _eop_id()}
        results = _api_validate(client, params)
        assert [(r['uid'], r['reason']) for r in results] == [(advisor_uid, 'outside_peer_department')]

    def test_parent_privacy_wins(self, client, fake_auth):
        """A comment on a private note is judged as private even when the client says otherwise."""
        parent = _create_note(ce3_advisor_uid, author_dept_codes=('ZCEEE',), is_private=True)
        fake_auth.login(eop_manager_uid)
        results = _api_validate(client, {'uids': [advisor_uid], 'parentNoteId': parent.id, 'isPrivate': False})
        assert [r['reason'] for r in results] == ['private_note']

    def test_non_users_duplicates_and_order(self, client, fake_auth):
        """UIDs that aren't BOA users are skipped, a repeated UID is reported once, and results follow input order."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        params = {'uids': ['999999999', director_uid, int(deleted_uid), deleted_uid, director_uid], 'noteId': note.id}
        results = _api_validate(client, params)
        assert [(r['uid'], r['reason']) for r in results] == [(director_uid, 'self_tag'), (deleted_uid, 'deleted_user')]

    def test_result_shape(self, client, fake_auth):
        """Each invalid tag has uid, name, and reason, with the UID as a string."""
        fake_auth.login(director_uid)
        note = _create_note(director_uid)
        results = _api_validate(client, {'uids': [int(deleted_uid)], 'noteId': note.id})
        assert len(results) == 1
        assert set(results[0].keys()) == {'uid', 'name', 'reason'}
        assert results[0]['uid'] == deleted_uid
