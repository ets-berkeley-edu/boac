"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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


import re

from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.sis_advising import get_sis_advising_attachments, get_sis_advising_topics, resolve_sis_created_at, resolve_sis_updated_at
from boac.lib.util import get_benchmarker, join_if_present, search_result_text_snippet, TEXT_SEARCH_PATTERN
from boac.merged.calnet import get_calnet_users_for_csids, get_uid_for_csid
from boac.models.appointment import Appointment, appointment_event_to_json
from boac.models.appointment_read import AppointmentRead
from boac.models.authorized_user import AuthorizedUser
from dateutil.tz import tzutc
from flask import current_app as app
from flask_login import current_user

"""Provide advising appointment data from local and external sources."""


def get_advising_appointments(sid):
    benchmark = get_benchmarker(f'get_advising_appointments {sid}')
    benchmark('begin')
    appointments_by_id = {}
    benchmark('begin SIS advising appointments query')
    appointments_by_id.update(get_sis_advising_appointments(sid))
    benchmark('begin non legacy advising appointments query')
    appointments_by_id.update(get_non_legacy_advising_appointments(sid))
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
        appointments_by_id[appointment_id]['isLegacy'] = True
    return appointments_by_id


def get_non_legacy_advising_appointments(sid):
    appointments_by_id = {}
    for row in Appointment.get_appointments_per_sid(sid):
        appointment = row.__dict__
        appointment_id = appointment['id']
        event = appointment_event_to_json(appointment_id, row.status)
        appointments_by_id[str(appointment_id)] = appointment_to_compatible_json(
            appointment=appointment,
            topics=[t.to_api_json() for t in row.topics if not t.deleted_at],
            event=event,
        )
    return appointments_by_id


def search_advising_appointments(
    search_phrase,
    advisor_csid=None,
    advisor_uid=None,
    student_csid=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    offset=0,
    limit=20,
):
    benchmark = get_benchmarker('search_advising_appointments')
    benchmark('begin')

    if search_phrase:
        search_terms = [t.group(0) for t in list(re.finditer(TEXT_SEARCH_PATTERN, search_phrase)) if t]
        search_phrase = ' & '.join(search_terms)
    else:
        search_terms = []

    advisor_uid = get_uid_for_csid(app, advisor_csid) if (not advisor_uid and advisor_csid) else advisor_uid

    benchmark('begin local appointments query')
    appointments_feed = Appointment.search(
        search_phrase=search_phrase,
        advisor_uid=advisor_uid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        limit=limit,
        offset=offset,
    )
    benchmark('end local appointments query')

    local_appointments_count = len(appointments_feed)
    if local_appointments_count == limit:
        return appointments_feed

    benchmark('begin loch appointments query')
    loch_results = data_loch.search_advising_appointments(
        search_phrase=search_phrase,
        advisor_uid=advisor_uid,
        advisor_csid=advisor_csid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=max(0, offset - local_appointments_count),
        limit=(limit - local_appointments_count),
    )
    benchmark('end loch appointments query')

    benchmark('begin loch appointments parsing')
    appointments_feed += _get_loch_appointments_search_results(loch_results, search_terms)
    benchmark('end loch appointments parsing')

    return appointments_feed


def get_appointment_advisors(query_fragments, limit=None):
    appointment_advisors = Appointment.find_advisors_by_name(query_fragments, limit=limit)
    legacy_appointment_advisors = data_loch.match_appointment_advisors_by_name(query_fragments, limit=limit)
    advisors_feed = _local_advisor_feed(appointment_advisors) + _loch_advisor_feed(legacy_appointment_advisors)
    advisors_by_uid = {a.get('uid'): a for a in advisors_feed}
    return list(advisors_by_uid.values())


def appointment_to_compatible_json(appointment, topics=(), attachments=None, event=None):
    # We have legacy appointments and appointments created via BOA. The following sets a standard for the front-end.
    advisor_uid = appointment.get('advisor_uid')
    appointment_id = appointment.get('id')
    appointment_type = appointment.get('appointment_type')
    departments = []
    dept_codes = appointment.get('advisor_dept_codes') or []
    for dept_code in dept_codes:
        departments.append({
            'code': dept_code,
            'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code, dept_code),
        })
    api_json = {
        'id': appointment_id,
        'advisorId': AuthorizedUser.get_id_per_uid(advisor_uid) if advisor_uid else None,
        'advisorName': appointment.get('advisor_name') or join_if_present(
            ' ',
            [appointment.get('advisor_first_name'), appointment.get('advisor_last_name')],
        ),
        'advisorRole': appointment.get('advisor_role'),
        'advisorUid': appointment.get('advisor_uid'),
        'advisorDepartments': departments,
        'appointmentType': appointment_type,
        'attachments': attachments,
        'createdAt': resolve_sis_created_at(appointment),
        'createdBy': appointment.get('created_by'),
        'deptCode': appointment.get('dept_code'),
        'details': appointment.get('details'),
        'student': {
            'sid': appointment.get('student_sid'),
        },
        'topics': topics,
        'updatedAt': resolve_sis_updated_at(appointment),
        'updatedBy': appointment.get('updated_by'),
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
            'advisorDeptCodes': [dept['code'] for dept in advisor_feed.get('departments')],
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


def _local_advisor_feed(local_results):
    return [
        {
            'label': a.get('advisor_name'),
            'uid': a.get('advisor_uid'),
        } for a in local_results
    ]


def _loch_advisor_feed(loch_results):
    return [
        {
            'label': f"{a.get('first_name')} {a.get('last_name')}",
            'uid': a.get('uid'),
        } for a in loch_results
    ]
