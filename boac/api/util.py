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

import json
from datetime import datetime

from flask import current_app as app
from flask import request
from flask_login import current_user

from boac.api.errors import BadRequestError, ResourceNotFoundError, UnauthorizedRequestError
from boac.externals.data_loch import get_sis_holds
from boac.lib.berkeley import ACADEMIC_STANDING_DESCRIPTIONS, dept_codes_where_advising
from boac.lib.util import get_benchmarker, is_int, join_if_present, process_input_from_rich_text_editor, to_iso_format, utc_now
from boac.merged import calnet
from boac.merged.advising_appointment import get_advising_appointments
from boac.merged.advising_note import can_current_user_access_note, can_current_user_edit_note, get_advising_notes, note_to_compatible_json
from boac.merged.calnet import get_calnet_user_for_uid
from boac.merged.cohort_filter_options import PROTECTED_COHORT_FILTERS_COENG, PROTECTED_COHORT_FILTERS_UWASC, CohortFilterOptions
from boac.merged.sis_terms import current_term_id
from boac.models.alert import Alert
from boac.models.appointment_read import AppointmentRead
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.comment import Comment
from boac.models.comment_parent import EFORM_COMMENT_PARENT_TYPES
from boac.models.comment_read import CommentRead
from boac.models.curated_group import CuratedGroup
from boac.models.degree_progress_course import ACCENT_COLOR_CODES
from boac.models.note import Note, note_contact_type_enum
from boac.models.note_read import NoteRead
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.university_dept import UniversityDept
from boac.models.user_login import UserLogin


def can_access_admitted_students(user):
    return user.is_authenticated and (current_user.is_admin or _is_advisor_in_department(current_user, 'ZCEEE'))


def normalize_accent_color(color):
    if color:
        capitalized = color.capitalize()
        return capitalized if capitalized in list(ACCENT_COLOR_CODES.keys()) else None


def add_alert_counts(alert_counts, students):
    students_by_sid = {student['sid']: student for student in students}
    for alert_count in alert_counts:
        student = students_by_sid.get(alert_count['sid'], None)
        if student:
            student.update({
                'alertCount': alert_count['alertCount'],
            })
    return students


def authorized_users_api_feed(users, sort_by='lastName', sort_descending=False):
    if not users:
        return ()
    calnet_users = calnet.get_calnet_users_for_uids(app, [u.uid for u in users])
    profiles = []
    peer_advising_memberships_by_user_id = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_ids(
        authorized_user_ids=[user.id for user in users],
    )
    university_depts_by_id = dict((d['id'], d) for d in UniversityDept.get_all_departments())
    for user in users:
        profile = calnet_users[user.uid]
        if not profile:
            continue
        if not profile.get('name'):
            profile['name'] = ((profile.get('firstName') or '') + ' ' + (profile.get('lastName') or '')).strip()

        profile.update({
            'id': user.id,
            'automateDegreeProgressPermission': user.automate_degree_progress_permission,
            'canAccessAdvisingData': user.can_access_advising_data and bool(profile['name']),
            'canAccessCanvasData': user.can_access_canvas_data,
            'canEditDegreeProgress': user.degree_progress_permission == 'read_write' or user.is_admin,
            'canReadDegreeProgress': user.degree_progress_permission in ['read', 'read_write'] or user.is_admin,
            'createdAt': to_iso_format(user.created_at),
            'degreeProgressPermission': user.degree_progress_permission,
            'deletedAt': to_iso_format(user.deleted_at),
            'departments': [],
            'disabledAt': to_iso_format(user.disabled_at),
            'isAdmin': user.is_admin,
            'isBlocked': user.is_blocked,
        })
        for m in user.department_memberships:
            profile['departments'].append({
                **m.university_dept.to_api_json(),
                'memberships': [
                    {
                        'automateMembership': m.automate_membership,
                        'role': m.role,
                    },
                ],
            })

        for m in peer_advising_memberships_by_user_id.get(user.id, []):
            peer_advising_dept_membership = {
                'role': m['role_type'],
                'peerAdvisingDepartmentId': m['peer_advising_department_id'],
                'peerAdvisingDepartmentName': m['peer_advising_department_name'],
            }
            university_dept_id = m['university_dept_id']
            university_dept_api_json = next((d for d in profile['departments'] if d['id'] == university_dept_id), None)
            if university_dept_api_json:
                # If the university_dept was added in the 'for user.department_memberships' loop above
                # then we append the peer_advising membership to the existing object.
                university_dept_api_json['memberships'].append(peer_advising_dept_membership)
            else:
                profile['departments'].append({
                    **university_depts_by_id[university_dept_id],
                    'memberships': [peer_advising_dept_membership],
                })
        user_login = UserLogin.last_login(user.uid)
        profile['lastLogin'] = to_iso_format(user_login.created_at) if user_login else None
        profiles.append(profile)
    return sorted(profiles, key=lambda p: (p.get(sort_by) is None, p.get(sort_by)), reverse=sort_descending)


def can_current_user_view_cohort(cohort_owner_uid):
    # Admin users can view all cohorts. Non-admin can view all except cohorts owned by Admins.
    return not cohort_owner_uid or current_user.is_admin or not AuthorizedUser.is_admin_user(cohort_owner_uid)


def construct_phantom_cohort(domain, filters, **kwargs):
    # A "phantom" cohort is an unsaved search.
    cohort = CohortFilter(
        domain=domain,
        name=f'phantom_cohort_{datetime.now().timestamp()}',
        filter_criteria=translate_filters_to_cohort_criteria(filters, domain),
    )
    return cohort.to_api_json(**kwargs)


def invalidate_parent_read_after_external_comment(parent_type, parent_id, viewer_id):
    if parent_type == 'appointment':
        AppointmentRead.delete_for_appointment_except_viewer(
            appointment_id=parent_id,
            keep_viewer_id=viewer_id,
        )
    elif parent_type in EFORM_COMMENT_PARENT_TYPES:
        NoteRead.delete_for_note(parent_id, except_viewer_id=viewer_id)


def mark_comments_read_for_parent(viewer_id, parent_id, parent_types):
    """Mark all Comment rows for parent_id across one or more comment_parent types as read."""
    pairs = [(pt, str(parent_id)) for pt in parent_types]
    grouped = Comment.get_comments_by_parents(pairs)
    comment_ids = [c.id for group in grouped.values() for c in group]
    if comment_ids:
        CommentRead.find_or_create(viewer_id=viewer_id, comment_ids=comment_ids)
    return comment_ids


def record_external_comment_read_state(comment, viewer_id, parent_type, parent_id, *, after_edit=False):
    if after_edit:
        CommentRead.delete_for_comment(comment_id=comment.id, except_viewer_id=viewer_id)
    CommentRead.find_or_create(viewer_id=viewer_id, comment_ids=[comment.id])
    invalidate_parent_read_after_external_comment(parent_type, parent_id, viewer_id)


def create_note_comment(parent_note, params, peer_advising_department_id=None):
    body = process_input_from_rich_text_editor(params.get('body'))
    if not body or not body.strip():
        raise BadRequestError('Request has missing or invalid request parameters')
    attachments = get_note_attachments_from_http_post(tolerate_none=True)
    attachment_limit = app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE']
    if len(attachments) > attachment_limit:
        raise BadRequestError(f'No more than {attachment_limit} attachments may be uploaded at once.')
    author = get_note_author_profile_of_current_user()
    if not author['author_role']:
        raise UnauthorizedRequestError('Unauthorized.')
    comment = Note.create(
        **author,
        attachments=attachments,
        body=body,
        is_private=parent_note.is_private,
        parent_note_id=parent_note.id,
        peer_advising_department_id=peer_advising_department_id,
        sid=parent_note.sid,
        subject='',
    )
    NoteRead.delete_for_note(parent_note.id, except_viewer_id=current_user.get_id())
    NoteRead.find_or_create(viewer_id=current_user.get_id(), note_ids=[comment.id])
    return comment


def update_note_comment(params):
    comment_id = params.get('id')
    if not comment_id or not is_int(comment_id):
        raise BadRequestError('Request has missing or invalid request parameters')
    comment = Note.find_by_id(note_id=int(comment_id))
    if not comment or not comment.parent_note_id or not can_current_user_edit_note(comment):
        raise ResourceNotFoundError('Note not found')
    body = process_input_from_rich_text_editor(params.get('body'))
    if not body or not body.strip():
        raise BadRequestError('Request has missing or invalid request parameters')

    delete_ids_ = params.get('deleteAttachmentIds') or []
    delete_ids_ = delete_ids_ if isinstance(delete_ids_, list) else str(delete_ids_).split(',')
    delete_attachment_ids = [int(id_) for id_ in delete_ids_ if is_int(id_)]
    attachments = get_note_attachments_from_http_post(tolerate_none=True)
    attachment_limit = app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE']
    existing_attachment_count = len(comment.attachments) - len(delete_attachment_ids)
    if existing_attachment_count + len(attachments) > attachment_limit:
        raise BadRequestError(f'No more than {attachment_limit} attachments may be uploaded at once.')

    comment = Note.update(
        body=body,
        contact_type=comment.contact_type,
        is_draft=False,
        is_private=comment.is_private,
        note_id=comment.id,
        set_date=comment.set_date,
        sid=comment.sid,
        subject=comment.subject,
        topics=[topic.topic for topic in comment.topics],
        note_template_id=comment.note_template_id,
        updated_at=utc_now(),
    )
    for attachment_id in delete_attachment_ids:
        comment = Note.delete_attachment(
            note_id=comment.id,
            attachment_id=attachment_id,
        )
    for attachment in attachments:
        comment = Note.add_attachment(
            note_id=comment.id,
            attachment=attachment,
        )
    NoteRead.delete_for_note(comment.id, except_viewer_id=current_user.get_id())
    NoteRead.delete_for_note(comment.parent_note_id, except_viewer_id=current_user.get_id())
    return comment

def put_notifications(student):
    sid = student['sid']
    student['notifications'] = {
        'alert': [],
        'hold': [],
        'requirement': [],
    }
    if current_user.can_access_advising_data:
        student['notifications']['appointment'] = []
        student['notifications']['eForm'] = []
        student['notifications']['note'] = []
        for appointment in get_advising_appointments(sid) or []:
            message = appointment['details']
            student['notifications']['appointment'].append({
                **appointment,
                'message': message.strip() if message else None,
                'type': 'appointment',
            })

        # The front-end requires 'type', 'message' and 'read'. Optional fields: id, status, createdAt, updatedAt.
        notes_by_id = {}
        children = []
        for note in get_advising_notes(sid) or []:
            message = note['body']
            note_type = 'eForm' if note.get('eForm') else 'note'
            wrapped = {
                **note,
                'message': message.strip() if message else None,
                'type': note_type,
            }
            if note_type == 'eForm':
                student['notifications']['eForm'].append(wrapped)
                continue
            if wrapped.get('parentNoteId'):
                children.append(wrapped)
            else:
                wrapped['comments'] = []
                notes_by_id[wrapped['id']] = wrapped
                student['notifications']['note'].append(wrapped)
        for child in children:
            parent = notes_by_id.get(child['parentNoteId'])
            if parent:
                parent['comments'].append(child)
            else:
                student['notifications']['note'].append(child)
        for parent in notes_by_id.values():
            parent['comments'].sort(key=lambda c: c.get('createdAt') or '')
        _attach_external_comments(
            appointments=student['notifications']['appointment'],
            eforms=student['notifications']['eForm'],
        )
    for alert in Alert.current_alerts_for_sid(viewer_id=current_user.get_id(), sid=sid):
        student['notifications']['alert'].append({
            **alert,
            'id': alert['id'],
            'read': alert['dismissed'],
            'type': 'alert',
        })
    for row in get_sis_holds(sid):
        hold = json.loads(row['feed'])
        reason = hold.get('reason', {})
        student['notifications']['hold'].append({
            **hold,
            'createdAt': hold.get('fromDate'),
            'message': join_if_present('. ', [reason.get('description'), reason.get('formalDescription')]),
            'read': True,
            'type': 'hold',
        })
    degree_progress = student.get('sisProfile', {}).get('degreeProgress', {})
    if degree_progress:
        for requirement in degree_progress.get('requirements', {}).values():
            student['notifications']['requirement'].append({
                **requirement,
                'message': requirement['name'] + ' ' + requirement['status'],
                'read': True,
                'type': 'requirement',
            })


def _attach_external_comments(appointments, eforms):
    pairs = []
    for a in appointments:
        if a.get('id') is not None:
            pairs.append(('appointment', str(a['id'])))
    for e in eforms:
        parent_type = e.get('parentType')
        if parent_type and e.get('id') is not None:
            pairs.append((parent_type, str(e['id'])))
    grouped = Comment.get_comments_by_parents(pairs)
    all_comment_ids = [c.id for group in grouped.values() for c in group]
    reads_set = set()
    if all_comment_ids:
        read_rows = CommentRead.get_comments_read_by_user(current_user.get_id(), all_comment_ids)
        reads_set = {r.comment_id for r in read_rows}
    for a in appointments:
        if a.get('id') is None:
            a['comments'] = []
            continue
        a['comments'] = [c.to_api_json(read=c.id in reads_set) for c in grouped.get(('appointment', str(a['id'])), [])]
    for e in eforms:
        parent_type = e.get('parentType')
        if not parent_type or e.get('id') is None:
            e['comments'] = []
            continue
        e['comments'] = [c.to_api_json(read=c.id in reads_set) for c in grouped.get((parent_type, str(e['id'])), [])]


def get_current_user_profile():
    cohorts = []
    user_id = current_user.get_id()
    for cohort in CohortFilter.get_cohorts(user_id):
        cohort['isOwnedByCurrentUser'] = True
        cohorts.append(cohort)
    return {
        **current_user.to_api_json(),
        'myCohorts': cohorts,
        'myCuratedGroups': get_my_curated_groups(),
        'myDraftNoteCount': Note.get_draft_note_count(None if current_user.is_admin else current_user.uid),
        'preferences': {
            'admitSortBy': 'last_name',
            'sortBy': 'last_name',
            'termId': current_term_id(),
        },
    }


def get_note_attachments_from_http_post(tolerate_none=False):
    request_files = request.files
    attachments = []
    for index in range(app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE']):
        attachment = request_files.get(f'attachment[{index}]')
        if attachment:
            attachments.append(attachment)
        else:
            break
    if not tolerate_none and not len(attachments):
        raise BadRequestError('request.files is empty')
    byte_stream_bundle = []
    for attachment in attachments:
        filename = attachment.filename and attachment.filename.strip()
        if not filename:
            raise BadRequestError(f'Invalid file in request form data: {attachment}')
        else:
            byte_stream_bundle.append({
                'name': filename.rsplit('/', 1)[-1],
                'byte_stream': attachment.read(),
            })
    return byte_stream_bundle


def get_template_attachment_ids_from_http_post():
    ids = request.form.get('templateAttachmentIds', [])
    return ids if isinstance(ids, list) else list(filter(None, str(ids).split(',')))


def get_note_topics_from_http_post():
    arg = 'topics'
    topics = request.form.getlist(arg)
    if not topics and request.content_type == 'application/json':
        topics = request.get_json().get(arg)
    return topics if isinstance(topics, list) else list(filter(None, str(topics).split(',')))


def get_my_curated_groups():
    benchmark = get_benchmarker('my_curated_groups')
    curated_groups = []
    user_id = current_user.get_id()
    for curated_group in CuratedGroup.get_curated_groups(owner_id=user_id):
        students = [{'sid': sid} for sid in CuratedGroup.get_all_sids(curated_group.id)]
        students_with_alerts = Alert.include_alert_counts_for_students(
            benchmark=benchmark,
            viewer_user_id=user_id,
            group={'students': students},
            count_only=True,
        )
        curated_groups.append({
            **curated_group.to_api_json(include_students=False),
            'alertCount': sum(s['alertCount'] for s in students_with_alerts),
            'sids': [student['sid'] for student in students],
            'totalStudentCount': len(students),
        })
    return curated_groups


def is_unauthorized_domain(domain):
    if domain not in ['default', 'admitted_students']:
        raise BadRequestError(f'Invalid domain: {domain}')
    return (domain == 'admitted_students'
            and not current_user.is_admin
            and 'ZCEEE' not in dept_codes_where_advising(current_user.departments))


def is_unauthorized_search(filter_keys, order_by=None):
    filter_key_set = set(filter_keys)
    if list(filter_key_set & set(PROTECTED_COHORT_FILTERS_UWASC)) or order_by in ['group_name']:
        if not current_user.is_admin and 'UWASC' not in dept_codes_where_advising(current_user.departments):
            return True
    if list(filter_key_set & set(PROTECTED_COHORT_FILTERS_COENG)):
        if not current_user.is_admin and 'COENG' not in dept_codes_where_advising(current_user.departments):
            return True
    return False


def is_valid_date_string(date_string, date_format='%Y-%m-%d'):
    try:
        return parse_date_param(date_string, date_format) is not None
    except (TypeError, ValueError):
        return False


def parse_date_param(date_string, date_format='%Y-%m-%d'):
    return datetime.strptime(date_string, date_format).date() if date_string else None


def get_academic_standing(profile):
    academic_standing = profile.get('sisProfile', {}).get('academicStanding', {})
    status = academic_standing.get('status')
    if status:
        term_name = academic_standing.get('termName')
        status_name = ACADEMIC_STANDING_DESCRIPTIONS.get(status, status)
        return f"{status_name}{f', {term_name}' if term_name else ''}"
    else:
        return ''


def get_boac_note_as_compatible_json(note, note_read, children_by_parent_id=None):
    base = {
        **note_to_compatible_json(
            note=note.__dict__,
            note_read=note_read,
            attachments=[a.to_api_json() for a in note.attachments if not a.deleted_at],
            topics=[t.topic for t in note.topics if not t.deleted_at],
        ),
        'message': note.body,
        'type': 'note',
    }
    base['comments'] = get_boa_note_comments_as_compatible_json(note, children_by_parent_id)
    return base


def get_boa_note_comments_as_compatible_json(note, children_by_parent_id=None):
    if note.parent_note_id:
        return []
    if children_by_parent_id is None:
        child_notes = Note.get_notes_by_parent_id(parent_note_id=note.id)
        accessible = [c for c in child_notes if can_current_user_access_note(c)]
    else:
        accessible = children_by_parent_id.get(note.id, [])
    reads_by_id = {}
    if accessible:
        read_rows = NoteRead.get_notes_read_by_user(current_user.get_id(), [str(c.id) for c in accessible])
        reads_by_id = {r.note_id: r.created_at for r in read_rows}
    return[
        get_boac_note_as_compatible_json(
            child,
            note_read=reads_by_id.get(str(child.id)),
            children_by_parent_id=children_by_parent_id,
        )
        for child in accessible
    ]

def get_coe_status(profile):
    status = None
    if profile.get('coeProfile'):
        status = 'active' if profile.get('coeProfile').get('isActiveCoe') else 'inactive'
    return status


def get_college_advisors(profile):
    values = []
    for advisor in profile.get('advisors', []):
        last_name = advisor['lastName']
        uid = advisor['uid']
        if advisor.get('role', '').lower() == 'college advisor' and (last_name or uid):
            advisor_name = f"{advisor['firstName']} {last_name}" if last_name else f'UID:{uid}'
            values.append(advisor_name)
    return values


def get_current_user_cohorts_containing(profile, cohorts):
    sid = profile['sid']
    return [cohort['name'] for cohort in cohorts if sid in cohort['sids']]


def get_current_user_curated_groups_containing(profile, curated_groups):
    sid = profile['sid']
    return [curated_group['name'] for curated_group in curated_groups if sid in curated_group['sids']]


def get_note_author_profile_of_current_user():
    author = current_user.to_api_json()
    calnet_profile = get_calnet_user_for_uid(app, author['uid'])
    if calnet_profile and calnet_profile.get('departments'):
        dept_codes = [dept.get('deptCode') for dept in calnet_profile.get('departments')]
    else:
        dept_codes = dept_codes_where_advising(current_user.departments)
    role = None
    if calnet_profile and calnet_profile.get('title'):
        role = calnet_profile['title']
    elif current_user.departments:
        for department in current_user.departments:
            if len(department['memberships']):
                role = department['memberships'][0]['role']
    return {
        'author_uid': author['uid'],
        'author_name': author['name'],
        'author_role': role,
        'author_dept_codes': dept_codes,
    }


def translate_filters_to_cohort_criteria(filters, domain):
    db_type_per_key = get_cohort_filter_db_type_per_key(domain)
    criteria = {}
    for row in filters:
        key = row['key']
        db_type = db_type_per_key[key]
        if db_type == 'boolean':
            criteria[key] = row['value']
        elif db_type in ['string[]', 'json[]']:
            if not criteria.get(key):
                criteria[key] = []
            criteria[key].append(row['value'])
    return criteria


def validate_note_contact_type(contact_type):
    if contact_type and contact_type not in note_contact_type_enum.enums:
        raise BadRequestError('Unrecognized contact type')
    return contact_type


def get_cohort_filter_db_type_per_key(domain):
    filter_type_per_key = {}
    filter_categories = CohortFilterOptions.get_customized_filter_categories(
        domain=domain,
        owner_uid=current_user.uid,
    )
    for filter_category in filter_categories:
        for option in filter_category['options']:
            filter_type_per_key[option['key']] = option['type']['db']
    return filter_type_per_key


def _is_advisor_in_department(user, dept_code):
    is_advisor_in_department = False
    is_dict = isinstance(user, dict)
    is_authenticated = user['isAuthenticated'] if is_dict else user.is_authenticated
    departments = user['departments'] if is_dict else user.departments
    if is_authenticated:
        for department in departments:
            if dept_code == department['deptCode'] and next((m for m in department['memberships'] if m['role'] in ('advisor', 'director')), False):
                is_advisor_in_department = True
                break
    return is_advisor_in_department
