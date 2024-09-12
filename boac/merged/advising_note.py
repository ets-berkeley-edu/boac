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

import csv
from datetime import datetime
import io
from itertools import groupby
from operator import itemgetter
from os import path
import re

from boac.externals import data_loch, s3
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, term_name_for_sis_id
from boac.lib.sis_advising import (
    get_legacy_attachment_stream,
    get_sis_advising_attachments,
    get_sis_advising_topics,
    resolve_sis_created_at,
    resolve_sis_updated_at,
)
from boac.lib.util import (
    camelize,
    get_benchmarker,
    is_int,
    join_if_present,
    safe_strftime,
    search_result_text_snippet,
    TEXT_SEARCH_PATTERN,
)
from boac.merged.calnet import get_calnet_users_for_csids, get_uid_for_csid
from boac.models.note import Note
from boac.models.note_attachment import NoteAttachment
from boac.models.note_read import NoteRead
from dateutil.tz import tzutc
from flask import current_app as app
from flask_login import current_user
import pytz
import zipstream

"""Provide advising note data from local and external sources."""


def can_current_user_access_note(note):
    if isinstance(note, dict):
        is_draft = note['is_draft'] if 'is_draft' in note else note['isDraft']
    else:
        is_draft = note.is_draft
    return current_user.is_admin or \
        (current_user.can_access_advising_data and (not is_draft or get_author_uid(note) == current_user.uid))


def can_current_user_edit_note(note):
    return current_user.can_access_advising_data and get_author_uid(note) == current_user.uid


def get_advising_notes(sid, exclude_draft_notes=False):
    benchmark = get_benchmarker(f'get_advising_notes {sid}')
    benchmark('begin')
    notes_by_id = {}
    benchmark('begin SIS advising notes query')
    notes_by_id.update(get_sis_advising_notes(sid))
    benchmark('begin ASC advising notes query')
    notes_by_id.update(get_asc_advising_notes(sid))
    benchmark('begin Data Science advising notes query')
    notes_by_id.update(get_data_science_advising_notes(sid))
    benchmark('begin E&I advising notes query')
    notes_by_id.update(get_e_i_advising_notes(sid))
    benchmark('begin EOP advising notes query')
    notes_by_id.update(get_eop_advising_notes(sid))
    benchmark('begin History Dept advising notes query')
    notes_by_id.update(get_history_dept_advising_notes(sid))
    benchmark('begin native BOA advising notes query')
    native_boa_notes = get_native_boa_notes(exclude_draft_notes=exclude_draft_notes, sid=sid)
    for note_id in native_boa_notes:
        note = native_boa_notes[note_id]
        if can_current_user_access_note(note):
            notes_by_id[note_id] = note
    benchmark('begin SIS late drop eforms  query')
    notes_by_id.update(get_sis_late_drop_eforms(sid))
    if not notes_by_id.values():
        return None
    notes_read = NoteRead.get_notes_read_by_user(current_user.get_id(), notes_by_id.keys())
    for note_read in notes_read:
        note_feed = notes_by_id.get(note_read.note_id)
        if note_feed:
            note_feed['read'] = True
        else:
            app.logger.error(f'DB query mismatch for note id {note_read.note_id}')
    benchmark('end')
    return list(notes_by_id.values())


def get_sis_advising_notes(sid):
    notes_by_id = {}
    legacy_notes = data_loch.get_sis_advising_notes(sid)
    note_ids = [n['id'] for n in legacy_notes]
    legacy_topics = get_sis_advising_topics(note_ids)
    legacy_attachments = get_sis_advising_attachments(note_ids)
    for legacy_note in legacy_notes:
        note_id = legacy_note['id']
        notes_by_id[note_id] = note_to_compatible_json(
            note=legacy_note,
            topics=legacy_topics.get(note_id),
            attachments=legacy_attachments.get(note_id),
        )
        notes_by_id[note_id]['legacySource'] = 'SIS'
    return notes_by_id


def get_asc_advising_notes(sid):
    notes_by_id = {}
    legacy_topics = _get_asc_advising_note_topics(sid)
    for legacy_note in data_loch.get_asc_advising_notes(sid):
        note_id = legacy_note['id']
        legacy_note['dept_code'] = ['UWASC']
        notes_by_id[note_id] = note_to_compatible_json(
            note=legacy_note,
            topics=legacy_topics.get(note_id),
        )
        notes_by_id[note_id]['legacySource'] = 'ASC'
    return notes_by_id


def get_author_uid(note):
    return note.get('author_uid') or note['author']['uid'] if isinstance(note, dict) else note.author_uid


def get_data_science_advising_notes(sid):
    notes_by_id = {}
    for legacy_note in data_loch.get_data_science_advising_notes(sid):
        note_id = legacy_note['id']
        legacy_note['dept_code'] = ['DSDDO']
        notes_by_id[note_id] = note_to_compatible_json(
            note=legacy_note,
            topics=list(filter(None, [t.strip() for t in legacy_note.get('reason_for_appointment', '').split(',')])),
        )
        notes_by_id[note_id]['legacySource'] = 'Data Science'
    return notes_by_id


def get_e_i_advising_notes(sid):
    notes_by_id = {}
    legacy_topics = _get_e_i_advising_note_topics(sid)
    for legacy_note in data_loch.get_e_i_advising_notes(sid):
        note_id = legacy_note['id']
        legacy_note['dept_code'] = ['ZCEEE']
        notes_by_id[note_id] = note_to_compatible_json(
            note=legacy_note,
            topics=legacy_topics.get(note_id),
        )
        notes_by_id[note_id]['legacySource'] = 'CE3'
    return notes_by_id


def get_eop_advising_notes(sid):
    notes_by_id = {}
    topics = _get_eop_advising_note_topics(sid)
    for note in data_loch.get_eop_advising_notes(sid):
        note['dept_code'] = ['ZCEEE']
        note_id = note['id']
        attachments = None
        if note['attachment']:
            display_name = note['attachment']
            s3_name = f'{note_id}_{display_name}'
            attachments = [
                {
                    'id': note_id,
                    'displayName': display_name,
                    'fileName': s3_name,
                },
            ]
        notes_by_id[note_id] = note_to_compatible_json(
            note=note,
            topics=topics.get(note_id),
            attachments=attachments,
        )
        notes_by_id[note_id]['legacySource'] = 'EOP'
    return notes_by_id


def get_eop_attachment_stream(note_id):
    # Ensure the attachment ID is valid
    attachment = data_loch.get_eop_advising_note_attachment(note_id, include_private=current_user.can_access_private_notes)
    if not attachment:
        return None
    s3_key = '_'.join([note_id, attachment['display_name']])
    s3_key = '/'.join([app.config['DATA_LOCH_S3_EOP_NOTE_ATTACHMENTS_PATH'], s3_key])
    return {
        'filename': attachment['display_name'],
        'stream': s3.stream_object(app.config['DATA_LOCH_S3_EOP_ADVISING_NOTE_BUCKET'], s3_key),
    }


def get_history_dept_advising_notes(sid):
    notes_by_id = {}
    for note in data_loch.get_history_dept_advising_notes(sid):
        note['dept_code'] = ['SHIST']
        note_id = note['id']
        notes_by_id[note_id] = note_to_compatible_json(note=note)
        notes_by_id[note_id]['legacySource'] = 'History Dept'
    return notes_by_id


def get_native_boa_notes(sid, exclude_draft_notes=False):
    notes_by_id = {}
    for row in Note.get_notes_by_sid(exclude_draft_notes=exclude_draft_notes, sid=sid):
        note = row.__dict__
        if can_current_user_access_note(note):
            note_id = note['id']
            notes_by_id[str(note_id)] = note_to_compatible_json(
                note=note,
                attachments=[a.to_api_json() for a in row.attachments if not a.deleted_at],
                topics=[t.to_api_json() for t in row.topics if not t.deleted_at],
            )
    return notes_by_id


def get_sis_late_drop_eforms(sid):
    eforms_by_id = {}
    for eform in data_loch.get_sis_late_drop_eforms(sid):
        eform_id = eform['id']
        eforms_by_id[eform_id] = {
            **note_to_compatible_json(eform),
            **{'legacySource': 'SIS'},
        }
    return eforms_by_id


def search_advising_notes(
    search_phrase,
    author_csid=None,
    author_uid=None,
    student_csid=None,
    department_codes=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    offset=0,
    limit=20,
):
    benchmark = get_benchmarker('search_advising_notes')
    benchmark('begin')

    if search_phrase:
        search_terms = list({t.group(0) for t in list(re.finditer(TEXT_SEARCH_PATTERN, search_phrase)) if t})
        search_phrase = ' & '.join(search_terms)
    else:
        search_terms = []

    author_uid = get_uid_for_csid(app, author_csid) if (not author_uid and author_csid) else author_uid

    # TODO We're currently retrieving all results for the sake of subsequent offset calculations. As the number of notes in
    # BOA grows (and possibly requires us to use some kind of staging table for search indexing), we'll need to revisit.
    benchmark('begin local notes query')
    local_results = Note.search(
        search_phrase=search_phrase,
        author_uid=author_uid,
        student_csid=student_csid,
        department_codes=department_codes,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )
    benchmark('end local notes query')

    benchmark('begin local notes parsing')
    # Our offset calculations are unforuntately fussy because note parsing might reveal notes associated with students no
    # longer in BOA, which we won't include in the feed; so we don't actually know the length of our result set until parsing
    # is complete.
    total_boa_note_count = len(local_results)
    cutoff = min(total_boa_note_count, offset + limit)
    notes_feed = _get_local_notes_search_results(local_results, cutoff, search_terms)
    local_notes_count = len(notes_feed)
    notes_feed = notes_feed[offset:]

    benchmark('end local notes parsing')

    def _search_advising_notes(offset, limit):
        return data_loch.search_advising_notes(
            search_phrase=search_phrase,
            author_uid=author_uid,
            author_csid=author_csid,
            student_csid=student_csid,
            department_codes=department_codes,
            topic=topic,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            offset=offset,
            limit=limit,
        )

    # If the chunk of local (BOA) notes equals the 'limit' then return; no loch results needed.
    if len(notes_feed) == limit:
        # Here we query the data-loch for the sole purpose of extracting 'total_matching_count'.
        loch_results = _search_advising_notes(offset=0, limit=0)
        return {
            'notes': notes_feed,
            'totalNoteCount': total_boa_note_count + loch_results['total_matching_count'],
        }

    benchmark('begin loch notes query')
    loch_results = _search_advising_notes(offset=max(0, offset - local_notes_count), limit=(limit - len(notes_feed)))
    benchmark('end loch notes query')

    benchmark('begin loch notes parsing')
    notes_feed += _get_loch_notes_search_results(loch_results['rows'], search_terms)
    benchmark('end loch notes parsing')

    return {
        'notes': notes_feed,
        'totalNoteCount': total_boa_note_count + loch_results['total_matching_count'],
    }


def _get_local_notes_search_results(local_results, cutoff, search_terms):
    results = []
    student_rows = data_loch.get_basic_student_data([row.get('sid') for row in local_results])
    students_by_sid = {r.get('sid'): r for r in student_rows}
    for row in local_results:
        note = {camelize(key): row[key] for key in row.keys()}
        sid = note.get('sid')
        student_row = students_by_sid.get(sid, {})
        if student_row:
            omit_note_body = note.get('isPrivate') and not current_user.can_access_private_notes
            subject = note.get('subject')
            text = subject if omit_note_body else join_if_present(' - ', [subject, note.get('body')])
            results.append({
                'id': note.get('id'),
                'studentSid': sid,
                'studentUid': student_row.get('uid'),
                'studentName': join_if_present(' ', [student_row.get('first_name'), student_row.get('last_name')]),
                'advisorUid': note.get('authorUid'),
                'advisorName': note.get('authorName'),
                'noteSnippet': search_result_text_snippet(text, search_terms, TEXT_SEARCH_PATTERN),
                'createdAt': _isoformat(note, 'createdAt'),
                'updatedAt': _isoformat(note, 'updatedAt'),
            })
        if len(results) == cutoff:
            break
    return results


def _get_loch_notes_search_results(loch_results, search_terms):
    results = []
    if not loch_results:
        return results
    sids = list(set([row.get('advisor_sid') for row in loch_results if row.get('advisor_sid') is not None]))
    calnet_advisor_feeds = get_calnet_users_for_csids(app, sids)
    for note in loch_results:
        advisor_feed = calnet_advisor_feeds.get(note.get('advisor_sid'))
        if advisor_feed:
            advisor_name = advisor_feed.get('name') or join_if_present(' ', [advisor_feed.get('first_name'), advisor_feed.get('last_name')])
        else:
            advisor_name = None
        note_body = (note.get('note_body') or '').strip() or join_if_present(', ', [note.get('note_category'), note.get('note_subcategory')])
        results.append({
            'id': note.get('id'),
            'studentSid': note.get('sid'),
            'studentUid': note.get('uid'),
            'studentName': join_if_present(' ', [note.get('first_name'), note.get('last_name')]),
            'advisorSid': note.get('advisor_sid'),
            'advisorName': advisor_name or join_if_present(' ', [note.get('advisor_first_name'), note.get('advisor_last_name')]),
            'noteSnippet': search_result_text_snippet(note_body, search_terms, TEXT_SEARCH_PATTERN),
            'createdAt': resolve_sis_created_at(note),
            'updatedAt': resolve_sis_updated_at(note),
        })
    return results


def get_boa_attachment_stream(attachment):
    if attachment:
        path = attachment.path_to_attachment
        return {
            'filename': attachment.get_user_filename(),
            'stream': s3.stream_object(app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET'], path),
        }
    else:
        return None


def get_zip_stream(
        download_type,
        filename,
        notes,
        student,
):
    app_timezone = pytz.timezone(app.config['TIMEZONE'])
    is_eforms_download = download_type == 'eForm'
    notes = _filter_notes(download_type, notes)

    def iter_csv():
        def csv_line(_list):
            csv_output = io.StringIO()
            csv.writer(csv_output).writerow(_list)
            return csv_output.getvalue().encode('utf-8')
            csv_output.close()

        if is_eforms_download:
            csv_headers = [
                'student_sid',
                'student_name',
                'eform_id',
                'eform_type',
                'requested_action',
                'grading_basis',
                'requested_grading_basis',
                'units_taken',
                'requested_units_taken',
                'late_change_request_action',
                'late_change_request_status',
                'late_change_request_term',
                'late_change_request_course',
                'date_created',
                'updated_at',
            ]
        else:
            csv_headers = [
                'date_created',
                'student_sid',
                'student_name',
                'author_uid',
                'author_csid',
                'author_name',
                'subject',
                'body',
                'topics',
                'attachments',
                'is_private',
            ]

        yield csv_line(csv_headers)

        for note in notes:
            # strptime expects a timestamp without timezone; ancient date-only legacy notes get a bogus time appended.
            timestamp_created = f"{note['createdAt']}T12:00:00" if len(note['createdAt']) == 10 else note['createdAt'][:19]
            datetime_created = pytz.utc.localize(datetime.strptime(timestamp_created, '%Y-%m-%dT%H:%M:%S'))
            localized_created_at = datetime_created.astimezone(app_timezone).strftime('%Y-%m-%d')

            if is_eforms_download:
                e_form = note.get('eForm')
                section_id = e_form.get('sectionId')
                course = f"{e_form['sectionId']} {e_form['courseName']} - {e_form['courseTitle']} {e_form['section']}" if section_id else None
                column_data = [
                    student['sid'],
                    join_if_present(' ', [student.get('first_name', ''), student.get('last_name', '')]),
                    e_form.get('id'),
                    e_form.get('type'),
                    e_form.get('requestedAction'),
                    e_form.get('gradingBasis'),
                    e_form.get('requestedGradingBasis'),
                    e_form.get('unitsTaken'),
                    e_form.get('requestedUnitsTaken'),
                    e_form.get('action'),
                    e_form.get('status'),
                    term_name_for_sis_id(e_form.get('term')),
                    course,
                    localized_created_at,
                    e_form.get('updatedAt'),
                ]
            else:
                author_sids = [n['author']['sid'] for n in notes if n['author']['sid'] and not n['author']['name']]
                author_sids = list(set(author_sids))
                supplemental_calnet_advisor_feeds = get_calnet_users_for_csids(app, author_sids)
                author = supplemental_calnet_advisor_feeds.get(note['author']['sid']) or {}
                author_name = author.get('name') or join_if_present(' ', [author.get('firstName'), author.get('lastName')])
                author_uid = author.get('uid')

                omit_note_body = note.get('isPrivate') and not current_user.can_access_private_notes
                column_data = [
                    localized_created_at,
                    student['sid'],
                    join_if_present(' ', [student.get('first_name', ''), student.get('last_name', '')]),
                    (note['author']['uid'] or author_uid),
                    note['author']['sid'],
                    (note['author']['name'] or author_name),
                    note['subject'],
                    '' if omit_note_body else note['body'],
                    '; '.join([t for t in note['topics'] or []]),
                    '' if omit_note_body else '; '.join([a['displayName'] for a in note['attachments'] or []]),
                    note.get('isPrivate'),
                ]
            yield csv_line(column_data)

    z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
    csv_filename = f'{filename}.csv'
    z.write_iter(csv_filename, iter_csv())

    if notes:
        all_attachment_filenames = {csv_filename}
        for note in notes:
            if not note.get('isPrivate') or current_user.can_access_private_notes:
                for attachment in note['attachments'] or []:
                    is_legacy_attachment = not is_int(attachment['id'])
                    id_ = attachment['id'] if is_legacy_attachment else int(attachment['id'])
                    if is_legacy_attachment:
                        stream_data = get_legacy_attachment_stream(id_)
                    else:
                        attachment = NoteAttachment.find_by_id(id_)
                        stream_data = get_boa_attachment_stream(attachment)
                    if stream_data:
                        attachment_filename = stream_data['filename']
                        basename, extension = path.splitext(attachment_filename)
                        suffix = 1
                        while attachment_filename in all_attachment_filenames:
                            attachment_filename = f'{basename} ({suffix}){extension}'
                            suffix += 1
                        all_attachment_filenames.add(attachment_filename)
                        z.write_iter(attachment_filename, stream_data['stream'])
    return z


def note_to_compatible_json(
        note,
        topics=(),
        attachments=None,
        note_read=False,
):
    # We have legacy notes and notes created via BOAC. The following sets a standard for the front-end.
    departments = []
    dept_codes = note.get('dept_code') if 'dept_code' in note else note.get('author_dept_codes') or []
    for dept_code in dept_codes:
        departments.append({
            'code': dept_code,
            'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code, dept_code),
        })
    omit_note_body = note.get('is_private') and not current_user.can_access_private_notes
    return {
        'appointmentId': note.get('appointmentId'),
        'attachments': None if omit_note_body else attachments,
        'author': {
            'id': note.get('author_id'),
            'uid': note.get('author_uid'),
            'sid': note.get('advisor_sid'),
            'name': note.get('author_name'),
            'role': note.get('author_role'),
            'departments': departments,
            'email': note.get('advisor_email'),
        },
        'body': None if omit_note_body else note.get('body') or note.get('note_body'),
        'category': note.get('note_category'),
        'contactType': note.get('contact_type'),
        'createdAt': resolve_sis_created_at(note),
        'createdBy': note.get('created_by'),
        'eForm': _eform_to_json(note) if note.get('eform_id') else None,
        'id': note.get('id'),
        'isPrivate': note.get('is_private') or False,
        'isDraft': note.get('is_draft'),
        'read': True if note_read else False,
        'setDate': safe_strftime(note.get('set_date'), '%Y-%m-%d'),
        'sid': note.get('sid'),
        'subcategory': note.get('note_subcategory'),
        'subject': note.get('subject'),
        'topics': topics,
        'updatedAt': resolve_sis_updated_at(note),
        'updatedBy': note.get('updated_by'),
    }


def _eform_to_json(eform):
    return {
        'action': eform.get('requested_action'),
        'courseName': eform.get('course_display_name'),
        'courseTitle': eform.get('course_title'),
        'gradingBasis': eform.get('grading_basis_description'),
        'id': eform.get('eform_id'),
        'requestedAction': eform['requested_action'],
        'requestedGradingBasis': eform.get('requested_grading_basis_description'),
        'requestedUnitsTaken': eform.get('requested_units_taken'),
        'section': eform.get('section_num'),
        'sectionId': eform.get('section_id'),
        'status': eform.get('eform_status'),
        'term': eform.get('term_id'),
        'type': eform.get('eform_type'),
        'unitsTaken': eform.get('units_taken'),
        'updatedAt': eform.get('updated_at').astimezone(pytz.timezone(app.config['TIMEZONE'])).strftime('%Y-%m-%d'),
    }


def _filter_notes(download_type, notes):
    def _filter_rule(note):
        is_eform = bool(note.get('eForm', False))
        return is_eform if download_type == 'eForm' else not is_eform
    return list(filter(_filter_rule, notes))


def _get_asc_advising_note_topics(sid):
    topics = data_loch.get_asc_advising_note_topics(sid)
    topics_by_id = {}
    for advising_note_id, topics in groupby(topics, key=itemgetter('id')):
        topics_by_id[advising_note_id] = [topic['topic'] for topic in topics]
    return topics_by_id


def _get_e_i_advising_note_topics(sid):
    topics = data_loch.get_e_i_advising_note_topics(sid)
    topics_by_id = {}
    for advising_note_id, topics in groupby(topics, key=itemgetter('id')):
        topics_by_id[advising_note_id] = [topic['topic'] for topic in topics]
    return topics_by_id


def _get_eop_advising_note_topics(sid):
    topics = data_loch.get_eop_advising_note_topics(sid)
    topics_by_id = {}
    for advising_note_id, topics in groupby(topics, key=itemgetter('id')):
        topics_by_id[advising_note_id] = [topic['topic'] for topic in topics]
    return topics_by_id


def _isoformat(obj, key):
    value = obj.get(key)
    return value and value.astimezone(tzutc()).isoformat()
