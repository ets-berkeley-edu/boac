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

# Rules for tagging users (@<UID>) in note bodies. This module is the single home of those rules: save-time
# validation and the tagging autocomplete both call into it, so the autocomplete can never suggest someone
# the save would reject.

from collections.abc import Iterable
from dataclasses import dataclass

from flask import current_app as app

from boac.api.errors import UserTagValidationError
from boac.lib.util import find_user_tag_uids, replace_user_tags
from boac.merged.calnet import get_calnet_users_for_uids
from boac.models.authorized_user import AuthorizedUser
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.user_tag import UserTag

# Reason codes returned to the client for a tag that is not allowed.
DELETED_USER = 'deleted_user'
BATCH_NOTE = 'batch_note'
PRIVATE_NOTE = 'private_note'
NO_ACCESS = 'no_access'
SELF_TAG = 'self_tag'
OUTSIDE_PEER_DEPARTMENT = 'outside_peer_department'

# Shown in place of a tag whose person has no CalNet name.
UNKNOWN_USER_NAME = 'Unknown user'


@dataclass(frozen=True)
class TagContext:
    """The facts about a note and its writer that decide who may be tagged.

    A peer advisor manager is staff, not a peer, so the outside-department rule must not limit them. Callers set
    `writer_peer_department_id` with `writer_peer_department_id()` below, which returns it only for a `peer_advisor`.
    """

    writer_uid: str
    is_private: bool = False
    is_batch: bool = False
    # The note's peer advising department. For a note comment, the parent note's department.
    note_peer_department_id: int | None = None
    writer_peer_department_id: int | None = None


def writer_peer_department_id(user_id: int, peer_department_id: int | None) -> int | None:
    """Return the department that limits whom this writer may tag, or None when nothing limits them.

    Only an active `peer_advisor` of the note's peer department is limited to that group. Save-time validation and
    the tagging autocomplete must both build their context with this function, so the two never disagree.
    """
    if peer_department_id is None:
        return None
    memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(authorized_user_id=user_id)
    is_peer_advisor_here = any(
        m['role_type'] == 'peer_advisor' and m['peer_advising_department_id'] == peer_department_id for m in memberships
    )
    return peer_department_id if is_peer_advisor_here else None


def get_tagged_users_by_body(bodies: list[str | None]) -> list[dict[str, dict | None]]:
    """Return one {uid: {'name': name} | None} map per body, resolving every body's tags with one lookup.

    A tag is a UID with an `authorized_users` row, deleted users included. A tag with no CalNet name maps to None. Bodies
    with no `@digits` text cost no query, so most responses pay nothing.
    """
    uids_by_body = [find_user_tag_uids(body) for body in bodies]
    all_uids = {uid for uids in uids_by_body for uid in uids}
    if not all_uids:
        return [{} for _ in bodies]
    existing = AuthorizedUser.get_existing_uids(all_uids)
    if not existing:
        return [{} for _ in bodies]
    calnet_users = get_calnet_users_for_uids(app, sorted(existing))
    # Resolve each tag once, then hand each body only the tags it contains.
    users_by_uid = {uid: ({'name': calnet_users[uid]['name']} if (calnet_users.get(uid) or {}).get('name') else None) for uid in existing}
    return [{uid: users_by_uid[uid] for uid in uids if uid in users_by_uid} for uids in uids_by_body]


def get_tagged_user_names(body: str | None) -> dict[str, dict | None]:
    """Return the tagged-users map for a single body."""
    return get_tagged_users_by_body([body])[0]


def replace_tags_with_names(body: str | None, tagged_users: dict[str, dict | None]) -> str:
    """Turn each tag in `tagged_users` into @Name for downloads, and leave other @digits text alone."""

    def _name_for(uid):
        if uid not in tagged_users:
            return None
        user = tagged_users[uid]
        return f"@{user['name'] if user else UNKNOWN_USER_NAME}"

    return replace_user_tags(body, _name_for)


def get_tagged_uids(body: str | None) -> list[str]:
    """Return the UIDs tagged in the body that belong to BOA users, deleted ones included, in body order."""
    uids = find_user_tag_uids(body)
    existing = AuthorizedUser.get_existing_uids(uids)
    # Digits after an @ with no matching user are ordinary text, not a tag.
    return [uid for uid in uids if uid in existing]


def find_invalid_tags(uids: Iterable[str], context: TagContext, new_uids: Iterable[str] | None = None) -> list[dict]:
    """Return {uid, reason} for each UID that may not be tagged, in input order, with the first failing rule as the reason.

    UIDs with no authorized_users row are not tags and are skipped. `new_uids` names the tags added by this save; the
    self-tag and peer-department rules apply to those only. None means every UID is new.
    """
    # A UID tagged twice is one tag, so it is judged and reported once.
    uids = list(dict.fromkeys(str(uid) for uid in uids))
    new_uid_set = None if new_uids is None else {str(uid) for uid in new_uids}
    # One query covers every UID, since a save may carry many tags.
    eligibility = AuthorizedUser.get_tag_eligibility(uids)
    return _invalid_tags(uids, eligibility, context, new_uid_set)


def find_invalid_tags_with_names(uids: Iterable[str], context: TagContext) -> list[dict]:
    """Return {uid, name, reason} for each UID that may not be tagged in this context, treating every UID as newly added.

    The editor's tag check uses this to warn before Publish. It has no saved tags to compare against, so the self-tag and
    peer-department rules judge every UID, as they would on a first save.
    """
    invalid = find_invalid_tags(uids, context)
    # Skip the CalNet lookup when there is no one to name, which is the usual answer while the author types.
    return _with_names(invalid) if invalid else []


def note_tag_context(writer_uid: str, writer_id: int, peer_department_id: int | None, is_private: bool, is_batch: bool = False) -> TagContext:  # noqa: FBT001
    """Build the context for a note, a draft, or a new peer note from facts the server trusts.

    The tag endpoints and every save site build their context here, so autocomplete, validation and save never disagree.
    """
    return TagContext(
        writer_uid=writer_uid,
        is_private=bool(is_private),
        is_batch=is_batch,
        note_peer_department_id=peer_department_id,
        writer_peer_department_id=writer_peer_department_id(writer_id, peer_department_id),
    )


def note_comment_tag_context(parent_note, writer_uid: str, writer_id: int) -> TagContext:
    """Build the context for a comment on a note. Its privacy and peer department always come from the parent note."""
    return note_tag_context(writer_uid, writer_id, parent_note.peer_advising_department_id, parent_note.is_private)


def comment_tag_context(writer_uid: str) -> TagContext:
    """Build the context for an appointment or eForm comment, which is never private, never batch, and has no peer department."""
    return TagContext(writer_uid=writer_uid)


def validate_tags(body: str | None, context: TagContext, object_id: int | None = None, object_type: str | None = None) -> list[int]:
    """Raise UserTagValidationError if the body tags anyone who may not be tagged here; otherwise return their user ids.

    Pass the object id and type when editing a saved note or comment: the self-tag and peer-department rules then judge
    only tags added in this save, so a tag saved earlier never blocks an edit. Call this before writing anything.
    """
    uids = list(dict.fromkeys(find_user_tag_uids(body)))
    if not uids:
        return []
    eligibility = AuthorizedUser.get_tag_eligibility(uids)
    existing_user_ids = UserTag.get_active_user_ids(object_id, object_type) if object_id is not None else set()
    new_uid_set = {uid for uid, facts in eligibility.items() if facts['id'] not in existing_user_ids}
    invalid = _invalid_tags(uids, eligibility, context, new_uid_set)
    if invalid:
        raise UserTagValidationError(_with_names(invalid))
    # Digits after an @ with no matching user are ordinary text, not a tag, so they get no row.
    return [eligibility[uid]['id'] for uid in uids if uid in eligibility]


def validate_tags_for_private_thread(bodies: Iterable[str | None], writer_uid: str, peer_department_id: int | None) -> None:
    """Raise UserTagValidationError if making a note private would leave anyone tagged in these bodies unable to read it.

    Used for a published note's comments when the note turns private. Only the rules about the note apply (deleted user,
    private note, no access): those tags were already saved, so the rules about who added them do not.
    """
    uids = list(dict.fromkeys(uid for body in bodies for uid in find_user_tag_uids(body)))
    if not uids:
        return
    context = TagContext(writer_uid=writer_uid, is_private=True, note_peer_department_id=peer_department_id)
    invalid = find_invalid_tags(uids, context, new_uids=[])
    if invalid:
        raise UserTagValidationError(_with_names(invalid))


def sync_tags(object_id: int, object_type: str, user_ids: Iterable[int]) -> None:
    """Make the active user_tag rows of a saved note or comment match the people its body tags.

    Run this after the save itself has been written. A failure here is logged and swallowed, so the save still succeeds.
    """
    user_ids = list(dict.fromkeys(user_ids))
    try:
        for user_id in user_ids:
            UserTag.create(user_id=user_id, object_id=object_id, object_type=object_type)
        # A tag removed in this edit loses its row. A tag added back later gets a new row, so the person hears about it again.
        UserTag.delete_for_object(object_id, object_type, except_user_ids=user_ids)
    except Exception:
        # Log the id only: never the body or who was tagged.
        app.logger.exception(f'Failed to sync user tags for {object_type} {object_id}')


def search_taggable_users(snippet: str | None, context: TagContext, limit: int = 8) -> list[dict]:
    """Return up to `limit` users whose name contains the snippet and who may be tagged as new tags on this note.

    Results are {uid, name, title, deptName}, sorted by name without regard to case. A blank snippet or a batch note
    returns an empty list.
    """
    snippet = (snippet or '').strip()
    if not snippet or context.is_batch:
        return []
    peer_department_ids = [i for i in (context.note_peer_department_id, context.writer_peer_department_id) if i is not None]
    # One BOA query does the work of the old three: it names the candidates, filters them by their cached CalNet name,
    # and brings back their eligibility flags and cached feeds. Each query is a network round trip, and this runs on
    # every pause in typing.
    candidates = AuthorizedUser.get_tag_candidates(snippet, peer_department_ids)
    # Judge each candidate with the same rule function the save uses, so the search can never suggest someone the save would reject.
    taggable = [c for c in candidates if _first_failing_reason(c['uid'], c, context, True) is None]
    feeds = {c['uid']: c['calnet'] for c in taggable if c['calnet']}
    # Only people CalNet hasn't been asked about yet need a second step, and then only for those few.
    uncached_uids = [c['uid'] for c in taggable if not c['calnet']]
    if uncached_uids:
        feeds.update(get_calnet_users_for_uids(app, uncached_uids))
    needle = snippet.casefold()
    matches = []
    for uid, feed in feeds.items():
        name = feed.get('name')
        # The database narrowed the cached names with LOWER(); this final check uses casefold(), as the save does, and
        # also judges the names just fetched. A user CalNet cannot name cannot be shown in the autocomplete.
        if name and needle in name.casefold():
            departments = feed.get('departments') or []
            matches.append({
                'uid': uid,
                'name': name,
                'title': feed.get('title'),
                'deptName': departments[0].get('deptName') if departments else None,
            })
    # The UID breaks ties between equal names, so the order, and which match is cut at the limit, never varies.
    matches.sort(key=lambda m: (m['name'].casefold(), m['uid']))
    return matches[:limit]


def _invalid_tags(uids: list[str], eligibility: dict, context: TagContext, new_uid_set: set[str] | None) -> list[dict]:
    # Judge each tag with the shared rules. UIDs with no authorized_users row are not tags and are skipped.
    invalid = []
    for uid in uids:
        if uid not in eligibility:
            continue
        is_new = new_uid_set is None or uid in new_uid_set
        reason = _first_failing_reason(uid, eligibility[uid], context, is_new)
        if reason:
            invalid.append({'uid': uid, 'reason': reason})
    return invalid


def _with_names(invalid_tags: list[dict]) -> list[dict]:
    # The editor names each rejected tag. One CalNet lookup covers them all; a user with no CalNet name gets None.
    calnet_users = get_calnet_users_for_uids(app, [tag['uid'] for tag in invalid_tags])
    return [{'uid': tag['uid'], 'name': (calnet_users.get(tag['uid']) or {}).get('name'), 'reason': tag['reason']} for tag in invalid_tags]


def _first_failing_reason(uid: str, eligibility: dict, context: TagContext, is_new: bool) -> str | None:  # noqa: FBT001
    """Apply the rules in order and return the first one the candidate fails, or None if the tag is allowed.

    `eligibility` is the candidate's value from `AuthorizedUser.get_tag_eligibility`. The UID is passed separately because
    the self-tag rule compares it with the writer's.
    """
    reason = _note_rule_failure(eligibility, context)
    # The remaining rules judge the writer's new choices, so a tag saved earlier never blocks an edit.
    return reason or (_new_tag_rule_failure(uid, eligibility, context) if is_new else None)


def _note_rule_failure(eligibility: dict, context: TagContext) -> str | None:
    """Check rules 1 to 4, which depend only on the candidate and the note, not on who is adding the tag."""
    if eligibility['is_deleted']:
        return DELETED_USER
    if context.is_batch:
        return BATCH_NOTE
    # Private notes are visible to CE3 staff only.
    if context.is_private and not eligibility['is_ce3']:
        return PRIVATE_NOTE
    is_note_peer = context.note_peer_department_id is not None and context.note_peer_department_id in eligibility['peer_department_ids']
    can_read = (eligibility['is_advisor_or_director'] and eligibility['can_access_advising_data']) or is_note_peer
    return None if can_read else NO_ACCESS


def _new_tag_rule_failure(uid: str, eligibility: dict, context: TagContext) -> str | None:
    """Check rules 5 and 6, which apply only to tags the writer is adding in this save."""
    if uid == context.writer_uid:
        return SELF_TAG
    # Only a writer acting as a peer advisor is confined to their own department; managers have no writer_peer_department_id.
    if context.writer_peer_department_id is not None and context.writer_peer_department_id not in eligibility['peer_department_ids']:
        return OUTSIDE_PEER_DEPARTMENT
    return None
