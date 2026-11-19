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

from flask import current_app as app
from flask import request
from flask_login import current_user

from boac.api.decorators import advisor_or_peer_advisor_required
from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError, UnauthorizedRequestError
from boac.lib.http import tolerant_jsonify
from boac.lib.util import to_bool_or_none
from boac.merged.advising_note import can_current_user_access_note, can_current_user_edit_note
from boac.merged.user_tag import TagContext, search_taggable_users, writer_peer_department_id
from boac.models.comment_parent import comment_parent_type_enum
from boac.models.note import Note
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember

# Longer than any name; caps the work a single keystroke can ask for.
SNIPPET_MAX_LENGTH = 100


@app.route('/api/users/taggable', methods=['POST'])
@advisor_or_peer_advisor_required
def find_taggable_users():
    # The decorator already requires a login (an API key alone gets 401). Check again here because a tag search is
    # always run as a person, so it must never run without one even if the decorator changes.
    if not current_user.is_authenticated:
        raise UnauthorizedRequestError('Login required')
    params = request.get_json(silent=True)
    params = {} if params is None else params
    # Resolve first: it rejects a body that isn't a JSON object before anything reads from it.
    context = _resolve_tag_context(params)
    snippet = params.get('snippet')
    # A non-string snippet is treated as blank, which returns no one. Never log the snippet: it may hold a name.
    snippet = snippet.strip()[:SNIPPET_MAX_LENGTH] if isinstance(snippet, str) else ''
    return tolerant_jsonify(search_taggable_users(snippet, context))


def _resolve_tag_context(params):
    """Build the tag context from the editor's locator, after checking the caller may use it.

    The taggable-users and tag-validation endpoints share this, so both see the same access checks and context.
    """
    if not isinstance(params, dict):
        raise BadRequestError('Request body must be a JSON object.')
    note_id = params.get('noteId')
    parent_note_id = params.get('parentNoteId')
    peer_department_id = params.get('peerAdvisingDepartmentId')
    comment_parent_type = params.get('commentParentType')
    comment_parent_id = params.get('commentParentId')
    has_comment_locator = comment_parent_type is not None or comment_parent_id is not None
    locator_count = sum(1 for value in (note_id, parent_note_id, peer_department_id) if value is not None) + int(has_comment_locator)
    if locator_count != 1:
        raise BadRequestError('Exactly one tag context is required.')
    is_private = to_bool_or_none(params.get('isPrivate')) or False
    recipient_count = params.get('recipientCount')
    is_batch = recipient_count is not None and _to_int(recipient_count, 'recipientCount') > 1
    caller_id = current_user.get_id()

    if note_id is not None:
        note = Note.find_by_id(note_id=_to_int(note_id, 'noteId'))
        # A note the caller can't edit gets the same 404 as a missing one, so callers can't probe which note ids exist.
        if not note or not can_current_user_edit_note(note):
            raise ResourceNotFoundError('Note not found')
        if note.parent_note_id:
            # A note comment is judged by its parent thread, so the client's privacy can't widen a private thread.
            parent = Note.find_by_id(note_id=note.parent_note_id)
            if not parent:
                raise ResourceNotFoundError('Note not found')
            return _note_comment_context(parent, caller_id)
        # The editor's privacy counts here: the author may have just toggled it without saving.
        return TagContext(
            writer_uid=current_user.uid,
            is_private=is_private,
            is_batch=is_batch,
            note_peer_department_id=note.peer_advising_department_id,
            writer_peer_department_id=writer_peer_department_id(caller_id, note.peer_advising_department_id),
        )
    if parent_note_id is not None:
        parent = Note.find_by_id(note_id=_to_int(parent_note_id, 'parentNoteId'))
        if not parent or not can_current_user_access_note(parent):
            raise ResourceNotFoundError('Note not found')
        return _note_comment_context(parent, caller_id)
    if peer_department_id is not None:
        peer_department_id = _to_int(peer_department_id, 'peerAdvisingDepartmentId')
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(authorized_user_id=caller_id)
        if not any(m['peer_advising_department_id'] == peer_department_id for m in memberships):
            raise ForbiddenRequestError('You are not a member of this peer advising department.')
        return TagContext(
            writer_uid=current_user.uid,
            is_private=is_private,
            is_batch=is_batch,
            note_peer_department_id=peer_department_id,
            writer_peer_department_id=writer_peer_department_id(caller_id, peer_department_id),
        )
    # Appointment and eForm comments: never private, never batch, no peer department.
    if comment_parent_type not in comment_parent_type_enum.enums or comment_parent_id is None or not str(comment_parent_id).strip():
        raise BadRequestError('A valid comment parent type and id are required.')
    if not current_user.can_access_advising_data:
        raise ForbiddenRequestError('You are not authorized to comment here.')
    return TagContext(writer_uid=current_user.uid)


def _note_comment_context(parent, caller_id):
    # A note comment takes its privacy and peer department from the parent note, whatever the client sends.
    return TagContext(
        writer_uid=current_user.uid,
        is_private=parent.is_private,
        note_peer_department_id=parent.peer_advising_department_id,
        writer_peer_department_id=writer_peer_department_id(caller_id, parent.peer_advising_department_id),
    )


def _to_int(value, name):
    # Accept an int or a numeric string; bools are ints in Python but never a valid id or count here.
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    # isdigit() alone accepts characters like '²' that int() rejects, so require plain ASCII digits.
    if isinstance(value, str) and value.strip().isascii() and value.strip().isdigit():
        return int(value.strip())
    raise BadRequestError(f'Invalid {name}')
