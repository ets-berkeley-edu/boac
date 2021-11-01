"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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
    localize_datetime,
    search_result_text_snippet,
    TEXT_SEARCH_PATTERN,
    utc_now,
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


def get_advising_notes(sid):
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
    benchmark('begin non legacy advising notes query')
    notes_by_id.update(get_non_legacy_advising_notes(sid))
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


def get_non_legacy_advising_notes(sid):
    notes_by_id = {}
    for row in Note.get_notes_by_sid(sid):
        note = row.__dict__
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
        eforms_by_id[eform_id] = note_to_compatible_json(eform)
        eforms_by_id[eform_id]['legacySource'] = 'SIS'
    return eforms_by_id


def search_advising_notes(
    search_phrase,
    author_csid=None,
    author_uid=None,
    student_csid=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    offset=0,
    limit=20,
):
    benchmark = get_benchmarker('search_advising_notes')
    benchmark('begin')

    if search_phrase:
        search_terms = [t.group(0) for t in list(re.finditer(TEXT_SEARCH_PATTERN, search_phrase)) if t]
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
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )
    benchmark('end local notes query')

    benchmark('begin local notes parsing')
    # Our offset calculations are unforuntately fussy because note parsing might reveal notes associated with students no
    # longer in BOA, which we won't include in the feed; so we don't actually know the length of our result set until parsing
    # is complete.
    cutoff = min(len(local_results), offset + limit)
    notes_feed = _get_local_notes_search_results(local_results, cutoff, search_terms)
    local_notes_count = len(notes_feed)
    notes_feed = notes_feed[offset:]

    benchmark('end local notes parsing')

    if len(notes_feed) == limit:
        return notes_feed

    benchmark('begin loch notes query')
    loch_results = data_loch.search_advising_notes(
        search_phrase=search_phrase,
        author_uid=author_uid,
        author_csid=author_csid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=max(0, offset - local_notes_count),
        limit=(limit - len(notes_feed)),
    )
    benchmark('end loch notes query')

    benchmark('begin loch notes parsing')
    notes_feed += _get_loch_notes_search_results(loch_results, search_terms)
    benchmark('end loch notes parsing')

    return notes_feed


def _get_local_notes_search_results(local_results, cutoff, search_terms):
    results = []
    student_rows = data_loch.get_basic_student_data([row.get('sid') for row in local_results])
    students_by_sid = {r.get('sid'): r for r in student_rows}
    for row in local_results:
        note = {camelize(key): row[key] for key in row.keys()}
        sid = note.get('sid')
        student_row = students_by_sid.get(sid, {})
        if student_row:
            text = join_if_present(' - ', [note.get('subject'), note.get('body')])
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


def get_boa_attachment_stream(attachment_id):
    attachment = NoteAttachment.find_by_id(attachment_id)
    if attachment:
        path = attachment.path_to_attachment
        return {
            'filename': attachment.get_user_filename(),
            'stream': s3.stream_object(app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET'], path),
        }
    else:
        return None


def get_zip_stream_for_sid(sid):
    z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
    notes = get_advising_notes(sid)
    if not notes:
        return None

    filename = 'advising_notes'
    student_data = data_loch.get_basic_student_data([sid])
    if student_data:
        student_row = student_data[0]
        student_name = join_if_present(' ', [student_row.get('first_name'), student_row.get('last_name')])
        filename = '_'.join([filename, student_row.get('first_name', '').lower(), student_row.get('last_name', '').lower()])
    else:
        student_name = ''
    filename = '_'.join([filename, localize_datetime(utc_now()).strftime('%Y%m%d')])

    supplemental_calnet_advisor_feeds = get_calnet_users_for_csids(
        app,
        list(set([note['author']['sid'] for note in notes if note['author']['sid'] and not note['author']['name']])),
    )

    app_timezone = pytz.timezone(app.config['TIMEZONE'])

    def iter_csv():
        def csv_line(_list):
            csv_output = io.StringIO()
            csv.writer(csv_output).writerow(_list)
            return csv_output.getvalue().encode('utf-8')
            csv_output.close()

        yield csv_line([
            'date_created',
            'student_sid',
            'student_name',
            'author_uid',
            'author_csid',
            'author_name',
            'subject',
            'topics',
            'attachments',
            'body',
            'late_change_request_action',
            'late_change_request_status',
            'late_change_request_term',
            'late_change_request_course',
        ])
        for note in notes:
            calnet_author = supplemental_calnet_advisor_feeds.get(note['author']['sid'])
            if calnet_author:
                calnet_author_name =\
                    calnet_author.get('name') or join_if_present(' ', [calnet_author.get('firstName'), calnet_author.get('lastName')])
                calnet_author_uid = calnet_author.get('uid')
            else:
                calnet_author_name = None
                calnet_author_uid = None
            # strptime expects a timestamp without timezone; ancient date-only legacy notes get a bogus time appended.
            timestamp_created = f"{note['createdAt']}T12:00:00" if len(note['createdAt']) == 10 else note['createdAt'][:19]
            datetime_created = pytz.utc.localize(datetime.strptime(timestamp_created, '%Y-%m-%dT%H:%M:%S'))
            date_local = datetime_created.astimezone(app_timezone).strftime('%Y-%m-%d')
            e_form = note.get('eForm') or {}
            yield csv_line([
                date_local,
                sid,
                student_name,
                (note['author']['uid'] or calnet_author_uid),
                note['author']['sid'],
                (note['author']['name'] or calnet_author_name),
                note['subject'],
                '; '.join([t for t in note['topics'] or []]),
                '; '.join([a['displayName'] for a in note['attachments'] or []]),
                note['body'],
                e_form.get('action'),
                e_form.get('status'),
                term_name_for_sis_id(e_form.get('term')),
                f"{e_form['sectionId']} {e_form['courseName']} - {e_form['courseTitle']} {e_form['section']}" if e_form.get('sectionId') else None,
            ])
    z.write_iter(f'{filename}.csv', iter_csv())

    all_attachment_filenames = set()
    all_attachment_filenames.add(f'{filename}.csv')
    for note in notes:
        for attachment in note['attachments'] or []:
            is_legacy_attachment = not is_int(attachment['id'])
            id_ = attachment['id'] if is_legacy_attachment else int(attachment['id'])
            stream_data = get_legacy_attachment_stream(id_) if is_legacy_attachment else get_boa_attachment_stream(id_)
            if stream_data:
                attachment_filename = stream_data['filename']
                basename, extension = path.splitext(attachment_filename)
                suffix = 1
                while attachment_filename in all_attachment_filenames:
                    attachment_filename = f'{basename} ({suffix}){extension}'
                    suffix += 1
                all_attachment_filenames.add(attachment_filename)
                z.write_iter(attachment_filename, stream_data['stream'])

    return {
        'filename': f'{filename}.zip',
        'stream': z,
    }


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
        'attachments': attachments,
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
        'createdAt': resolve_sis_created_at(note),
        'createdBy': note.get('created_by'),
        'eForm': _eform_to_json(note),
        'id': note.get('id'),
        'isPrivate': note.get('is_private') or False,
        'read': True if note_read else False,
        'sid': note.get('sid'),
        'subcategory': note.get('note_subcategory'),
        'subject': note.get('subject'),
        'topics': topics,
        'updatedAt': resolve_sis_updated_at(note),
        'updatedBy': note.get('updated_by'),
    }


def _eform_to_json(eform):
    if eform.get('eform_id'):
        return {
            'id': eform.get('eform_id'),
            'term': eform.get('term_id'),
            'action': eform.get('requested_action'),
            'status': eform.get('eform_status'),
            'sectionId': eform.get('section_id'),
            'section': eform.get('section_num'),
            'courseName': eform.get('course_display_name'),
            'courseTitle': eform.get('course_title'),
            'gradingBasis': eform.get('grading_basis_description'),
            'requestedGradingBasis': eform.get('requested_grading_basis_description'),
        }


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


def _isoformat(obj, key):
    value = obj.get(key)
    return value and value.astimezone(tzutc()).isoformat()
