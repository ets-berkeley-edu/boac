"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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

from itertools import groupby
from operator import itemgetter

from boac.externals import data_loch, s3
from dateutil.tz import tzutc
from flask import current_app as app


"""A utility module collecting logic specific to SIS advising notes and appointments."""


def get_sis_advising_topics(ids):
    topics = data_loch.get_sis_advising_topics(ids)
    topics_by_id = {}
    for note_or_appointment_id, topics in groupby(topics, key=itemgetter('advising_note_id')):
        topics_by_id[note_or_appointment_id] = [topic['note_topic'] for topic in topics]
    return topics_by_id


def get_sis_advising_attachments(ids):
    attachments = data_loch.get_sis_advising_attachments(ids)
    attachments_by_id = {}

    def _attachment_to_json(attachment):
        sis_file_name = attachment.get('sis_file_name')
        return {
            'id': sis_file_name,
            'sisFilename': sis_file_name,
            'displayName': sis_file_name if attachment.get('created_by') == 'UCBCONVERSION' else attachment.get('user_file_name'),
        }
    for note_or_appointment_id, attachments in groupby(attachments, key=itemgetter('advising_note_id')):
        attachments_by_id[note_or_appointment_id] = [_attachment_to_json(a) for a in attachments]
    return attachments_by_id


def get_legacy_attachment_stream(filename):
    # Filenames come prefixed with SID by convention.
    for i, c in enumerate(filename):
        if not c.isdigit():
            break
    sid = filename[:i]
    if not sid:
        return None
    # Ensure that the file exists.
    attachment_result = data_loch.get_sis_advising_note_attachment(sid, filename)
    if not attachment_result or not attachment_result[0]:
        return None
    if attachment_result[0].get('created_by') == 'UCBCONVERSION':
        display_filename = filename
    else:
        display_filename = attachment_result[0].get('user_file_name')
    s3_key = '/'.join([app.config['DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH'], sid, filename])
    return {
        'filename': display_filename,
        'stream': s3.stream_object(app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET'], s3_key),
    }


def resolve_sis_created_at(note_or_appointment):
    if note_or_appointment.get('created_by') == 'UCBCONVERSION' or note_or_appointment.get('eform_id'):
        return note_or_appointment.get('created_at').date().isoformat()
    return _isoformat(note_or_appointment, 'created_at')


def resolve_sis_updated_at(note_or_appointment):
    # Notes and appointments converted from pre-CS legacy systems have an updated_at value indicating (probably)
    # time of conversion rather than an update by a human.
    if note_or_appointment.get('created_by') == 'UCBCONVERSION':
        return None
    else:
        updated_at = note_or_appointment.get('updated_at')
        created_at = note_or_appointment.get('created_at')
        if created_at and updated_at and _tzinfo(updated_at) == _tzinfo(created_at):
            return _isoformat(note_or_appointment, 'updated_at') if (updated_at - created_at).seconds else None
        else:
            return _isoformat(note_or_appointment, 'updated_at')


def _isoformat(obj, key):
    value = obj.get(key)
    return value and value.astimezone(tzutc()).isoformat()


def _tzinfo(_datetime):
    return _datetime and _datetime.tzinfo
