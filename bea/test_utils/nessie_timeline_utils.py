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

from bea.models.timeline_record_source import TimelineRecordSource
from bea.models.user import User
from boac.externals import data_loch
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
            'uid': uid,
            'sid': result[0]['sid'],
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
    return list(map(lambda r: r['sid'], results))


def get_sids_with_e_forms():
    sql = """SELECT DISTINCT sid
               FROM sis_advising_notes.student_late_drop_eforms"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: r['sid'], results))


def get_sids_with_sis_appts():
    sql = """SELECT DISTINCT sis_advising_notes.advising_appointments.sid
               FROM sis_advising_notes.advising_appointments
         INNER JOIN sis_advising_notes.advising_note_attachments
                 ON sis_advising_notes.advising_note_attachments.sid = sis_advising_notes.advising_appointments.sid
           ORDER BY sid ASC"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: r['sid'], results))


def get_sids_with_ycbm_appts():
    sql = """SELECT DISTINCT student_sid AS sid
               FROM boac_advising_appointments.ycbm_advising_appointments
              WHERE student_uid IS NOT NULL"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: r['sid'], results))
