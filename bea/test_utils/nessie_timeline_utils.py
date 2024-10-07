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
from itertools import groupby
import json
import re

from bea.models.alert import Alert
from bea.models.notes_and_appts.appointment import Appointment
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.note_attachment import NoteAttachment
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.models.user import User
from bea.test_utils import utils
from boac.externals import data_loch
from dateutil import parser
from flask import current_app as app


def get_advising_note_author(uid):
    sql = f"""SELECT sid,
                     first_name,
                     last_name
                FROM boac_advising_notes.advising_note_authors
               WHERE uid = '{uid}'"""
    app.logger.info(sql)
    result = data_loch.safe_execute_rds(sql)
    if result:
        data = {
            'uid': str(uid),
            'sid': str(result[0]['sid']),
            'first_name': result[0]['first_name'],
            'last_name': result[0]['last_name'],
        }
        return User(data=data)


def get_sids_with_notes_of_src(src, eop_private=False):
    if src == TimelineRecordSource.E_AND_I and eop_private:
        clause = """WHERE privacy_permissions = 'Note available only to CE3'
                      AND note IS NOT NULL
                      AND attachment IS NOT NULL"""
    elif src == TimelineRecordSource.E_AND_I:
        clause = """WHERE advisor_first_name != 'Reception'
                      AND advisor_last_name != 'Front Desk'"""

    elif src == TimelineRecordSource.SIS:
        clause = f"""INNER JOIN {src.value['schema']}.advising_note_attachments
                             ON {src.value['schema']}.advising_notes.sid = {src.value['schema']}.advising_note_attachments.sid"""
    else:
        clause = ''

    sql = f"""SELECT DISTINCT {src.value['schema']}.advising_notes.sid
                FROM {src.value['schema']}.advising_notes
                {clause}
            ORDER BY sid ASC;"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: str(r['sid']), results))


def get_sids_with_e_forms():
    sql = """SELECT DISTINCT sid
               FROM sis_advising_notes.student_late_drop_eforms"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: str(r['sid']), results))


# Student-specific notes


def get_asc_notes(student):
    sql = f"""SELECT boac_advising_asc.advising_notes.id AS id,
                     boac_advising_asc.advising_notes.created_at AS created_date,
                     boac_advising_asc.advising_notes.updated_at AS updated_date,
                     boac_advising_asc.advising_notes.advisor_uid AS advisor_uid,
                     boac_advising_asc.advising_notes.advisor_first_name AS advisor_first_name,
                     boac_advising_asc.advising_notes.advisor_last_name AS advisor_last_name,
                     boac_advising_asc.advising_notes.subject AS subject,
                     boac_advising_asc.advising_notes.body AS body,
                     json_agg(boac_advising_asc.advising_note_topics.topic) AS topics
                FROM boac_advising_asc.advising_notes
           LEFT JOIN boac_advising_asc.advising_note_topics
                  ON boac_advising_asc.advising_notes.id = boac_advising_asc.advising_note_topics.id
               WHERE boac_advising_asc.advising_notes.sid = '{student.sid}'
            GROUP BY advising_notes.id, created_date, advisor_uid, subject, body"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    notes = []
    for r in results:
        advisor = User({
            'uid': str(r['advisor_uid']),
            'first_name': r['advisor_first_name'],
            'last_name': r['advisor_last_name'],
        })
        note = Note({
            'advisor': advisor,
            'body': r['body'],
            'created_date': utils.date_to_local_tz(r['created_date']),
            'record_id': str(r['id']),
            'source': TimelineRecordSource.ASC,
            'student': student,
            'subject': r['subject'],
            'topics': r['topics'],
            'updated_date': utils.date_to_local_tz(r['updated_date']),
        })
        notes.append(note)
    return notes


def get_e_and_i_notes(student):
    sql = f"""SELECT boac_advising_e_i.advising_notes.id AS id,
                     boac_advising_e_i.advising_notes.advisor_uid AS advisor_uid,
                     boac_advising_e_i.advising_notes.advisor_first_name AS advisor_first_name,
                     boac_advising_e_i.advising_notes.advisor_last_name AS advisor_last_name,
                     boac_advising_e_i.advising_notes.overview AS subject,
                     boac_advising_e_i.advising_notes.note AS body,
                     boac_advising_e_i.advising_notes.created_at AS created_date,
                     boac_advising_e_i.advising_notes.updated_at AS updated_date,
                     boac_advising_e_i.advising_note_topics.topic AS topic
                FROM boac_advising_e_i.advising_notes
           LEFT JOIN boac_advising_e_i.advising_note_topics
                  ON boac_advising_e_i.advising_notes.id = boac_advising_e_i.advising_note_topics.id
               WHERE boac_advising_e_i.advising_notes.sid = '{student.sid}'
                 AND advisor_first_name != 'Reception'
                 AND advisor_last_name != 'Front Desk'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    notes = []
    grouped = groupby(results, key=lambda n: n['id'])
    for k, v in grouped:
        v = list(v)
        advisor = User({
            'uid': str(v[0]['advisor_uid']),
            'first_name': v[0]['advisor_first_name'],
            'last_name': v[0]['advisor_last_name'],
        })
        topics = []
        for t in v:
            if t['topic']:
                topics.append(t['topic'].upper())
        topics.sort()
        note = Note({
            'advisor': advisor,
            'body': (v[0]['body'] or ''),
            'created_date': utils.date_to_local_tz(v[0]['created_date']),
            'record_id': str(k),
            'source': TimelineRecordSource.E_AND_I,
            'subject': v[0]['subject'],
            'topics': topics,
            'updated_date': utils.date_to_local_tz(v[0]['updated_date']),
        })
        notes.append(note)
    return notes


def get_data_sci_notes(student):
    sql = f"""SELECT boac_advising_data_science.advising_notes.id AS id,
                     boac_advising_data_science.advising_notes.advisor_email AS advisor_email,
                     boac_advising_data_science.advising_notes.reason_for_appointment AS topics,
                     boac_advising_data_science.advising_notes.body AS body,
                     boac_advising_data_science.advising_notes.created_at AS created_date
                FROM boac_advising_data_science.advising_notes
               WHERE boac_advising_data_science.advising_notes.sid = '{student.sid}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    notes = []
    for r in results:
        created_date = utils.date_to_local_tz(parser.parse(r['created_date']))
        topics = r['topics'].split(', ')
        topics = list(map(lambda t: t.upper(), topics))
        topics.sort()
        note = Note({
            'body': r['body'],
            'created_date': created_date,
            'record_id': str(r['id']),
            'source': TimelineRecordSource.DATA,
            'topics': topics,
            'updated_date': created_date,
        })
        notes.append(note)
    return notes


def get_eop_notes(student):
    sql = f"""SELECT boac_advising_eop.advising_notes.id AS id,
                     boac_advising_eop.advising_notes.advisor_uid AS advisor_uid,
                     boac_advising_eop.advising_notes.advisor_first_name AS advisor_first_name,
                     boac_advising_eop.advising_notes.advisor_last_name AS advisor_last_name,
                     boac_advising_eop.advising_notes.overview AS subject,
                     boac_advising_eop.advising_notes.note AS body,
                     boac_advising_eop.advising_notes.privacy_permissions AS privacy,
                     boac_advising_eop.advising_notes.contact_method AS contact_type,
                     boac_advising_eop.advising_notes.created_at AS created_date,
                     boac_advising_eop.advising_note_topics.topic AS topic,
                     boac_advising_eop.advising_notes.attachment AS file_name
                FROM boac_advising_eop.advising_notes
           LEFT JOIN boac_advising_eop.advising_note_topics
                  ON boac_advising_eop.advising_notes.id = boac_advising_eop.advising_note_topics.id
               WHERE boac_advising_eop.advising_notes.sid = '{student.sid}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    notes = []
    grouped = groupby(results, key=lambda n: n['id'])
    for k, v in grouped:
        v = list(v)
        advisor = User({
            'uid': str(v[0]['advisor_uid']),
            'first_name': v[0]['advisor_first_name'],
            'last_name': v[0]['advisor_last_name'],
        })
        if v[0]['file_name']:
            attachment = NoteAttachment({
                'file_name': v[0]['file_name'],
                'attachment_id': str(v[0]['id']),
            })
        else:
            attachment = None
        created_date = utils.date_to_local_tz(parser.parse(v['created_date']))
        topics = []
        for t in v:
            if t['topic']:
                topics.append(t['topic'].upper())
        topics.sort()
        note = Note({
            'advisor': advisor,
            'attachment': [attachment],
            'body': v[0]['body'],
            'created_date': created_date,
            'is_private': (v[0]['privacy'] == 'Note available only to CE3'),
            'record_id': str(v[0]['id']),
            'source': TimelineRecordSource.EOP,
            'subject': v[0]['subject'],
            'topics': topics,
            'contact_type': v[0]['contact_type'],
            'updated_date': created_date,
        })
        notes.append(note)
    return notes


def get_history_notes(student):
    sql = f"""SELECT boac_advising_history_dept.advising_notes.id AS id,
                     boac_advising_history_dept.advising_notes.advisor_uid AS advisor_uid,
                     boac_advising_history_dept.advising_notes.note AS body,
                     boac_advising_history_dept.advising_notes.created_at AS created_date
                FROM boac_advising_history_dept.advising_notes
               WHERE boac_advising_history_dept.advising_notes.sid = '{student.sid}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    notes = []
    for r in results:
        advisor = User({'uid': str(r['advisor_uid'])})
        created_date = utils.date_to_local_tz(parser.parse(r['created_date']))
        note = Note({
            'advisor': advisor,
            'body': r['body'],
            'created_date': created_date,
            'record_id': str(r['id']),
            'source': TimelineRecordSource.HISTORY,
            'updated_date': created_date,
        })
        notes.append(note)
    return notes


def get_sis_notes(student):
    sql = f"""SELECT sis_advising_notes.advising_notes.id AS id,
                     sis_advising_notes.advising_notes.note_category AS category,
                     sis_advising_notes.advising_notes.note_subcategory AS subcategory,
                     sis_advising_notes.advising_notes.note_body AS body,
                     sis_advising_notes.advising_notes.created_by AS advisor_uid,
                     sis_advising_notes.advising_notes.advisor_sid AS advisor_sid,
                     sis_advising_notes.advising_notes.created_at AS created_date,
                     sis_advising_notes.advising_notes.updated_at AS updated_date,
                     sis_advising_notes.advising_note_topics.note_topic AS topic,
                     sis_advising_notes.advising_note_attachments.sis_file_name AS sis_file_name,
                     sis_advising_notes.advising_note_attachments.user_file_name AS user_file_name
                FROM sis_advising_notes.advising_notes
           LEFT JOIN sis_advising_notes.advising_note_topics
                  ON sis_advising_notes.advising_notes.id = sis_advising_notes.advising_note_topics.advising_note_id
           LEFT JOIN sis_advising_notes.advising_note_attachments
                  ON sis_advising_notes.advising_notes.id = sis_advising_notes.advising_note_attachments.advising_note_id
               WHERE sis_advising_notes.advising_notes.sid = '{student.sid}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    notes = []
    grouped = groupby(results, key=lambda n: n['id'])
    for k, v in grouped:
        v = list(v)
        advisor = User({'uid': str(v[0]['advisor_uid'])})
        attachment_data = []
        for r in v:
            if r['sis_file_name']:
                file_data = {
                    'sis_file_name': r['sis_file_name'],
                    'file_name': (r['sis_file_name'] if r['advisor_uid'] == 'UCBCONVERSION' else r['user_file_name']),
                }
                if file_data not in attachment_data:
                    attachment_data.append(file_data)
        attachments = [NoteAttachment(a) for a in attachment_data]
        source_body_empty = True if not v[0]['body'] or not v[0]['body'].strip() else False
        if source_body_empty:
            sub_cat = f" {v[0]['subcategory']}" if v[0]['subcategory'] else ''
            body = f"{v[0]['category']}{sub_cat}"
        else:
            body = v[0]['body'].replace('&Tab;', '')
        created_date = v[0]['created_date']
        updated_date = created_date if advisor.uid == 'UCBCONVERSION' else v[0]['updated_date']
        topics = []
        for t in v:
            if t['topic']:
                topics.append(t['topic'].upper())
        topics.sort()
        note = Note({
            'record_id': str(k),
            'body': body,
            'source_body_empty': source_body_empty,
            'advisor': advisor,
            'created_date': utils.date_to_local_tz(created_date),
            'updated_date': utils.date_to_local_tz(updated_date),
            'topics': topics,
            'attachments': attachments,
            'source': TimelineRecordSource.SIS,
        })
        notes.append(note)
    return notes


# APPOINTMENTS


def get_sis_appts(student):
    sql = f"""SELECT sis_advising_notes.advising_appointments.id AS id,
                     sis_advising_notes.advising_appointments.note_body AS body,
                     sis_advising_notes.advising_appointments.created_by AS advisor_uid,
                     sis_advising_notes.advising_appointments.advisor_sid,
                     sis_advising_notes.advising_appointments.created_at AS created_date,
                     sis_advising_notes.advising_appointments.updated_at AS updated_date,
                     sis_advising_notes.advising_appointment_advisors.first_name,
                     sis_advising_notes.advising_appointment_advisors.last_name,
                     sis_advising_notes.advising_note_topics.note_topic AS topic,
                     sis_advising_notes.advising_note_attachments.sis_file_name,
                     sis_advising_notes.advising_note_attachments.user_file_name
                FROM sis_advising_notes.advising_appointments
           LEFT JOIN sis_advising_notes.advising_appointment_advisors
                  ON sis_advising_notes.advising_appointments.advisor_sid = sis_advising_notes.advising_appointment_advisors.sid
           LEFT JOIN sis_advising_notes.advising_note_topics
                  ON sis_advising_notes.advising_appointments.id = sis_advising_notes.advising_note_topics.advising_note_id
           LEFT JOIN sis_advising_notes.advising_note_attachments
                  ON sis_advising_notes.advising_appointments.id = sis_advising_notes.advising_note_attachments.advising_note_id
               WHERE sis_advising_notes.advising_appointments.sid = '{student.sid}'
            ORDER BY id ASC"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    appts = []
    grouped = groupby(results, key=lambda n: n['id'])
    for k, v in grouped:
        v = list(v)
        advisor = User({
            'uid': str(v[0]['advisor_uid']),
            'sid': str(v[0]['advisor_sid']),
            'first_name': v[0]['first_name'],
            'last_name': v[0]['last_name'],
        })

        attachment_data = []
        for r in v:
            if r['sis_file_name']:
                file_data = {
                    'sis_file_name': r['sis_file_name'],
                    'file_name': (r['sis_file_name'] if r['advisor_uid'] == 'UCBCONVERSION' else r['user_file_name']),
                }
                if file_data not in attachment_data:
                    attachment_data.append(file_data)
        attachments = [NoteAttachment(file_name=a['file_name'], data=a) for a in attachment_data]

        body = v[0]['body'].replace('&Tab;', '').strip()

        topics = []
        for t in v:
            if t['topic']:
                topics.append(t['topic'].upper())
        topics.sort()

        created_date = v[0]['created_date']
        updated_date = created_date if advisor.uid == 'UCBCONVERSION' else v[0]['updated_date']

        appts.append(Appointment({
            'record_id': str(k),
            'advisor': advisor,
            'attachments': attachments,
            'created_date': utils.date_to_local_tz(created_date),
            'detail': body,
            'source': TimelineRecordSource.SIS,
            'student': student,
            'topics': topics,
            'updated_date': utils.date_to_local_tz(updated_date),
        }))
    return appts


def get_ycbm_appts(student):
    sql = f"""SELECT boac_advising_appointments.ycbm_advising_appointments.id,
                     boac_advising_appointments.ycbm_advising_appointments.appointment_type,
                     boac_advising_appointments.ycbm_advising_appointments.title,
                     boac_advising_appointments.ycbm_advising_appointments.details,
                     boac_advising_appointments.ycbm_advising_appointments.advisor_name,
                     boac_advising_appointments.ycbm_advising_appointments.starts_at,
                     boac_advising_appointments.ycbm_advising_appointments.ends_at,
                     boac_advising_appointments.ycbm_advising_appointments.cancelled,
                     boac_advising_appointments.ycbm_advising_appointments.cancellation_reason
                FROM boac_advising_appointments.ycbm_advising_appointments
               WHERE boac_advising_appointments.ycbm_advising_appointments.student_sid = '{student.sid}'
            ORDER BY starts_at ASC"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    appts = []
    grouped = groupby(results, key=lambda n: n['id'])
    for k, v in grouped:
        v = list(v)
        advisor = User({'full_name': v[0]['advisor_name']})
        cancel_reason = str(v[0]['cancellation_reason']).strip() or 'Canceled'
        appts.append(Appointment({
            'record_id': str(k),
            'advisor': advisor,
            'cancel_reason': cancel_reason,
            'created_date': utils.date_to_local_tz(v[0]['starts_at']),
            'detail': v[0]['details'],
            'end_time': utils.date_to_local_tz(v[0]['ends_at']),
            'source': TimelineRecordSource.YCBM,
            'start_time': utils.date_to_local_tz(v[0]['starts_at']),
            'status': ('Canceled' if v[0]['cancelled'] else ''),
            'student': student,
            'title': re.sub(r'\s+', ' ', str(v[0]['title'])).strip(),
            'contact_type': str(v[0]['appointment_type']).strip(),
        }))
    return appts


def get_sids_with_sis_appts():
    sql = """SELECT DISTINCT sis_advising_notes.advising_appointments.sid
               FROM sis_advising_notes.advising_appointments
         INNER JOIN sis_advising_notes.advising_note_attachments
                 ON sis_advising_notes.advising_note_attachments.sid = sis_advising_notes.advising_appointments.sid
           ORDER BY sid ASC"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: str(r['sid']), results))


def get_sids_with_ycbm_appts():
    sql = """SELECT DISTINCT student_sid AS sid
               FROM boac_advising_appointments.ycbm_advising_appointments
              WHERE student_uid IS NOT NULL"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: str(r['sid']), results))


# HOLDS


def get_student_holds(student):
    sql = f"""SELECT sid,
                     feed
                FROM student.student_holds
               WHERE sid = '{student.sid}'"""
    app.logger.info(sql)
    holds = []
    results = data_loch.safe_execute_rds(sql)
    for row in results:
        feed = json.loads(row['feed'])
        message = f"{feed['reason']['description']}. {feed['reason']['formalDescription']}".replace('\n', '')
        holds.append(Alert({
            'message': re.sub(r'\s+', ' ', message),
            'student': student,
        }))
    return holds
