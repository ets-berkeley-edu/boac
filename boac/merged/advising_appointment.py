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

from dateutil.tz import tzutc
from flask import current_app as app
from flask_login import current_user

from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.sis_advising import get_sis_advising_attachments, get_sis_advising_topics, resolve_sis_created_at, resolve_sis_updated_at
from boac.lib.util import TEXT_SEARCH_PATTERN, get_benchmarker, join_if_present, search_result_text_snippet
from boac.merged.advising_search import (
    build_comment_search_result,
    get_students_by_sid,
    merge_search_feed,
    parse_search_phrases,
    resolved_comment_total_count,
)
from boac.merged.calnet import get_calnet_users_for_csids, get_uid_for_csid
from boac.models.appointment_read import AppointmentRead
from boac.models.authorized_user import AuthorizedUser
from boac.models.comment import Comment

"""Provide advising appointment data from local and external sources."""


def get_advising_appointments(sid):
    benchmark = get_benchmarker(f'get_advising_appointments {sid}')
    benchmark('begin')
    appointments_by_id = {}
    benchmark('begin SIS advising appointments query')
    appointments_by_id.update(get_sis_advising_appointments(sid))
    benchmark('begin Calendly advising appointments query')
    appointments_by_id.update(get_calendly_advising_appointments(sid))
    benchmark('begin YCBM advising appointments query')
    appointments_by_id.update(get_ycbm_advising_appointments(sid))
    if not appointments_by_id.values():
        return None
    appointments_read = AppointmentRead.get_appointments_read_by_user(current_user.get_id(), appointments_by_id.keys())
    for appointment_read in appointments_read:
        appointment_feed = appointments_by_id.get(appointment_read.appointment_id)
        if appointment_feed:
            appointment_feed['read'] = True
        else:
            app.logger.error(f'DB query mismatch for appointment id {appointment_read.appointment_id}')
    benchmark('end')
    return list(appointments_by_id.values())


def get_calendly_advising_appointments(sid):
    appointments_by_id = {}
    for row in data_loch.get_calendly_advising_appointments(sid):
        appointment = row
        appointment_id = appointment['id']
        # NOTE: We intentionally ignore Calendly's 'meeting_notes_html' property because our service-lead wants advisors
        # to create and manage notes in BOA. If we were to show 'meeting_notes' in BOA then we might enable bad habits.
        details = None
        questions_and_answers = json.loads(appointment['questions_and_answers'] or '[]')
        if questions_and_answers:
            details = '<ul>'
            for q_and_a in questions_and_answers:
                details += f"<li><b>{q_and_a['question']}</b> {q_and_a['answer']}</li>"
            details += '</ul>'

        appointment['details'] = details
        api_json = appointment_to_compatible_json(appointment=appointment)
        api_json['isRescheduled'] = appointment['is_rescheduled']
        api_json['isStudentNoShow'] = appointment['is_student_no_show']
        appointments_by_id[str(appointment_id)] = api_json
    return appointments_by_id


def get_sis_advising_appointments(sid):
    appointments_by_id = {}
    legacy_appointments = data_loch.get_sis_advising_appointments(sid)
    appointment_ids = [a['id'] for a in legacy_appointments]
    legacy_topics = get_sis_advising_topics(appointment_ids)
    legacy_attachments = get_sis_advising_attachments(appointment_ids)
    for legacy_appointment in legacy_appointments:
        appointment_id = legacy_appointment['id']
        appointments_by_id[appointment_id] = appointment_to_compatible_json(
            appointment=legacy_appointment,
            topics=legacy_topics.get(appointment_id),
            attachments=legacy_attachments.get(appointment_id),
        )
        appointments_by_id[appointment_id]['legacySource'] = 'SIS'
    return appointments_by_id


def get_ycbm_advising_appointments(sid):
    appointments_by_id = {}
    for row in data_loch.get_ycbm_advising_appointments(sid):
        appointment = row
        appointment_id = appointment['id']
        appointments_by_id[str(appointment_id)] = appointment_to_compatible_json(
            appointment=appointment,
        )
    return appointments_by_id


def search_advising_appointments(
    search_phrase,
    advisor_csid=None,
    advisor_uid=None,
    student_csid=None,
    department_codes=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    offset=0,
    limit=20,
):
    benchmark = get_benchmarker('search_advising_appointments')
    benchmark('begin')

    search_terms = parse_search_phrases(search_phrase)
    if search_terms:
        search_phrase = ' & '.join(search_terms)
    else:
        search_phrase = ''

    advisor_uid = get_uid_for_csid(app, advisor_csid) if (not advisor_uid and advisor_csid) else advisor_uid

    fetch_limit = offset + limit
    benchmark('begin loch appointments query')
    loch_results = data_loch.search_advising_appointments(
        search_phrase=search_phrase,
        advisor_uid=advisor_uid,
        advisor_csid=advisor_csid,
        student_csid=student_csid,
        department_codes=department_codes,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=0,
        limit=fetch_limit,
    )
    benchmark('end loch appointments query')

    benchmark('begin  loch appointments parsing')
    body_feed = _get_loch_appointments_search_results(loch_results['rows'], search_terms)
    for row in body_feed:
        row['kind'] = 'appointment'
    benchmark('end loch appointments parsing')

    body_total = loch_results['total_matching_count']
    comment_feed = []
    comment_total = 0
    if not department_codes and not topic:
        benchmark('begin appointment comments query')
        comment_results = Comment.search_by_parent_types(
            parent_types=['appointment'],
            search_phrases=search_terms or None,
            author_uid=advisor_uid,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            offset=0,
            limit=fetch_limit,
        )
        benchmark('end appointment comments query')
        comment_feed = _get_appointment_comment_search_results(
            comment_results['rows'],
            search_terms,
            student_csid=student_csid,
        )
        comment_total = resolved_comment_total_count(comment_results, comment_feed, fetch_limit)

    appointments_feed = merge_search_feed(body_feed, comment_feed, offset, limit)
    return {
        'appointments': appointments_feed,
        'totalAppointmentCount': body_total + comment_total,
    }


def appointment_to_compatible_json(appointment, topics=(), attachments=None, event=None):
    # We have legacy appointments and appointments created via BOA. The following sets a standard for the front-end.
    advisor_sid = appointment.get('advisor_sid')
    advisor_uid = appointment.get('advisor_uid')
    appointment_id = appointment.get('id')
    appointment_type = appointment.get('appointment_type')
    cancelled = appointment.get('cancelled')
    departments = []
    dept_codes = appointment.get('advisor_dept_codes') or []
    created_by = appointment.get('created_by') or 'YCBM'

    for dept_code in dept_codes:
        departments.append({
            'deptCode': dept_code,
            'deptName': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code, dept_code),
        })
    starts_at = appointment.get('starts_at').isoformat() if appointment.get('starts_at') else None
    api_json = {
        'id': appointment_id,
        'advisor': {
            'id': AuthorizedUser.get_id_per_uid(advisor_uid) if advisor_uid else None,
            'name': appointment.get('advisor_name') or join_if_present(
                ' ',
                [appointment.get('advisor_first_name'), appointment.get('advisor_last_name')],
            ),
            'sid': advisor_sid,
            'title': appointment.get('advisor_role'),
            'uid': advisor_uid,
            'departments': departments,
        },
        'appointmentTitle': appointment.get('title'),
        'appointmentType': appointment_type,
        'attachments': attachments,
        'createdAt': resolve_sis_created_at(appointment) or starts_at,
        'createdBy': created_by,
        'deptCode': appointment.get('dept_code'),
        'details': appointment.get('details'),
        'endsAt': appointment.get('ends_at').isoformat() if created_by in ['Calendly', 'YCBM'] and appointment.get('ends_at') else None,
        'startsAt': starts_at,
        'student': {
            'sid': appointment.get('student_sid'),
        },
        'topics': topics,
        'updatedAt': resolve_sis_updated_at(appointment),
        'updatedBy': appointment.get('updated_by'),
        'cancelReason': appointment.get('cancellation_reason') if created_by in ['Calendly', 'YCBM'] else None,
        'status': 'cancelled' if cancelled else None,
    }
    if appointment_type and appointment_type == 'Scheduled':
        api_json.update({
            'scheduledTime': _isoformat(appointment, 'scheduled_time'),
            'studentContactInfo': appointment.get('student_contact_info'),
            'studentContactType': appointment.get('student_contact_type'),
        })
    if event:
        api_json.update(event)
    return api_json


def _get_appointment_comment_search_results(comment_rows, search_terms, student_csid=None):
    if not comment_rows:
        return []

    appointment_ids = [parent_id for _, _, parent_id in comment_rows]
    appointment_rows = data_loch.get_advising_appointments_by_ids(appointment_ids)
    appointments_by_id = {str(row.get('id')): row for row in appointment_rows}

    resolved_rows = []
    for comment, parent_type, parent_id in comment_rows:
        appointment = appointments_by_id.get(str(parent_id))
        if not appointment:
            continue
        sid = appointment.get('sid')
        if student_csid and sid != student_csid:
            continue
        details = (appointment.get('note_body') or '').strip() or join_if_present(
            ', ',
            [appointment.get('note_category'), appointment.get('note_subcategory')],
        )
        resolved_rows.append((comment, parent_type, parent_id, appointment, details))

    students_by_sid = get_students_by_sid([row[3].get('sid') for row in resolved_rows])
    results = []
    for comment, parent_type, parent_id, appointment, details in resolved_rows:
        row = build_comment_search_result(
            comment,
            parent_type,
            parent_id,
            search_terms,
            appointment.get('sid'),
            students_by_sid,
            kind='commentOnAppointment',
            extra_fields={
                'appointment': {
                    'id': appointment.get('id'),
                    'details': details,
                },
            },
        )
        if row:
            results.append(row)
    return results


def _get_loch_appointments_search_results(loch_results, search_terms):
    results = []
    if not loch_results:
        return results
    sids = list(set([row.get('advisor_sid') for row in loch_results if row.get('advisor_sid') is not None]))
    calnet_advisor_feeds = get_calnet_users_for_csids(app, sids)
    for appointment in loch_results:
        advisor_feed = calnet_advisor_feeds.get(appointment.get('advisor_sid'))
        if advisor_feed:
            advisor_name = advisor_feed.get('name') or join_if_present(' ', [advisor_feed.get('firstName'), advisor_feed.get('lastName')])
        else:
            advisor_name = None
        details = (appointment.get('note_body') or '').strip() or join_if_present(
            ', ',
            [appointment.get('note_category'), appointment.get('note_subcategory')],
        )
        student_sid = appointment.get('sid')
        results.append({
            'id': appointment.get('id'),
            'advisorName': advisor_name or join_if_present(' ', [appointment.get('advisor_first_name'), appointment.get('advisor_last_name')]),
            'advisorRole': advisor_feed.get('title'),
            'advisorUid': advisor_feed.get('uid'),
            'advisorDeptCodes': [d['deptCode'] for d in advisor_feed.get('departments')],
            'createdAt': resolve_sis_created_at(appointment),
            'details': details,
            'detailsSnippet': search_result_text_snippet(details, search_terms, TEXT_SEARCH_PATTERN),
            'studentSid': student_sid,
            'updatedAt': resolve_sis_updated_at(appointment),
            'student': {
                'uid': appointment.get('uid'),
                'firstName': appointment.get('first_name'),
                'lastName': appointment.get('last_name'),
                'sid': student_sid,
            },
        })
    return results


def _isoformat(obj, key):
    value = obj.get(key)
    return value and value.astimezone(tzutc()).isoformat()
