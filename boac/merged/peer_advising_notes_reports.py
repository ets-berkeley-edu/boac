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

from sqlalchemy import text

from boac import db
from boac.externals.data_loch import get_basic_student_data
from boac.lib.util import to_iso_format
from boac.models.peer_advising_department import PeerAdvisingDepartment


def get_peer_advising_department_note_counts():
    sql = """
      SELECT ud.dept_name, ud.dept_code, ud.id, COUNT(*) AS count
        FROM peer_advising_departments pd
        JOIN university_depts ud ON pd.university_dept_id = ud.id
        JOIN notes n ON n.peer_advising_department_id = pd.id
       WHERE n.deleted_at IS NULL
         AND n.is_draft IS FALSE
       GROUP BY ud.dept_name, ud.dept_code, ud.id
    """
    return [row for row in db.session.execute(text(sql)).mappings()]


def get_granular_peer_advising_department_note_counts(university_dept_id):
    sql = """
        SELECT
            pd.name,
            pd.university_dept_id,
            COUNT(n.id) AS count
        FROM peer_advising_departments pd
        LEFT JOIN notes n
          ON n.peer_advising_department_id = pd.id
             AND n.deleted_at IS NULL
             AND n.is_draft = FALSE
        WHERE pd.university_dept_id = :university_dept_id
        GROUP BY
            pd.name,
            pd.university_dept_id
    """
    params = {'university_dept_id': university_dept_id}
    return db.session.execute(text(sql), params).mappings()


def get_peer_advising_note_author_count(peer_advising_department_id=None):
    sql = """
        SELECT COUNT(DISTINCT au.uid) AS count
        FROM authorized_users au
        JOIN notes n ON
            n.peer_advising_department_id IS NOT NULL
            AND n.author_uid = au.uid
            AND n.deleted_at IS NULL
    """
    params = {}
    if peer_advising_department_id:
        sql += 'WHERE n.peer_advising_department_id = :peer_advising_department_id'
        params['peer_advising_department_id'] = peer_advising_department_id
    return db.session.execute(text(sql), params).mappings().first()['count']


def get_peer_advising_note_count_since(peer_advising_department_id, timeframe_month=None):
    sql = f"""
      SELECT COUNT(n.id) AS count
      FROM notes n
      WHERE
        n.peer_advising_department_id = :peer_advising_department_id
        AND n.deleted_at IS NULL
        {f" AND to_char(n.created_at, 'YYYY-MM') = '{timeframe_month}'" if timeframe_month else ''}
    """
    params = {'peer_advising_department_id': peer_advising_department_id}
    return db.session.execute(text(sql), params).mappings().first()['count']


def get_all_peer_advising_notes(peer_advising_department_id):
    peer_advising_department = PeerAdvisingDepartment.get_department_by_id(peer_advising_department_id)
    if peer_advising_department:
        sql = """
            SELECT
              n.*, t.topic
            FROM notes n
            LEFT JOIN note_topics t ON (n.id = t.note_id AND t.deleted_at IS NULL)
            WHERE TRUE
              AND n.deleted_at IS NULL
              AND n.is_draft IS FALSE
              AND n.peer_advising_department_id = :peer_advising_department_id
            GROUP BY n.id, t.topic
            ORDER BY n.updated_at DESC
        """
        notes = []
        params = {'peer_advising_department_id': peer_advising_department_id}
        for row in db.session.execute(text(sql), params).mappings():
            note_id = row['id']
            note = next((n for n in notes if n['id'] == note_id), None)
            if not note:
                note = {
                    'id': note_id,
                    'author_dept_codes': ', '.join(row['author_dept_codes']),
                    'author_uid': row['author_uid'],
                    'author_name': row['author_name'],
                    'author_role': row['author_role'],
                    'body': row['body'],
                    'contact_type': row['contact_type'],
                    'peer_advising_department_name': peer_advising_department.name,
                    'sid': row['sid'],
                    'student_first_name': None,
                    'student_last_name': None,
                    'topics': [],
                    'created_at': to_iso_format(row['created_at'])[:10],
                    'updated_at': to_iso_format(row['updated_at'])[:10],
                }
                notes.append(note)
            topic = row['topic']
            if topic and topic not in note['topics']:
                note['topics'].append(topic)

        distinct_sids = list(set([note['sid'] for note in notes]))
        students_by_sid = {row['sid']: row for row in get_basic_student_data(sids=distinct_sids)}
        for note in notes:
            del note['id']
            note['topics'] = ', '.join(note['topics'])
            student = students_by_sid.get(note['sid'])
            if student:
                note['student_first_name'] = student['first_name']
                note['student_last_name'] = student['last_name']
        return notes
    else:
        raise ValueError(f'Peer Advising Department {peer_advising_department_id} not found.')


def get_notes_created_by_peer_advisors(peer_advising_department_id, timeframe_month=None):
    peer_advisors_by_uid = {}
    sql = """
        SELECT au.id, au.uid, au.deleted_at
        FROM authorized_users au
        JOIN peer_advising_department_members pm ON pm.authorized_user_id = au.id
        WHERE peer_advising_department_id = :peer_advising_department_id AND role_type = 'peer_advisor';
    """
    params = {'peer_advising_department_id': peer_advising_department_id}
    for row in db.session.execute(text(sql), params).mappings():
        peer_advisors_by_uid[row['uid']] = {
            'deleted_at': row['deleted_at'],
            'notes': [],
            'uid': row['uid'],
        }

    sql = f"""
        SELECT
          n.id AS note_id,
          n.author_uid,
          n.created_at,
          au.deleted_at
        FROM notes n
        LEFT JOIN authorized_users au ON au.uid = n.author_uid
        WHERE
          n.peer_advising_department_id = :peer_advising_department_id
          AND n.author_role = 'peer_advisor'
          AND n.deleted_at IS NULL
          {f" AND to_char(n.created_at, 'YYYY-MM') = '{timeframe_month}'" if timeframe_month else ''}
        ORDER BY n.created_at DESC
    """
    for row in db.session.execute(text(sql), params).mappings():
        uid = row['author_uid']
        peer_advisor = peer_advisors_by_uid[uid] if uid in peer_advisors_by_uid else None
        if not peer_advisor:
            peer_advisor = {
                'deleted_at': row['deleted_at'],
                'notes': [],
                'uid': uid,
            }
            peer_advisors_by_uid[uid] = peer_advisor
        peer_advisor['notes'].append({
            'id': row['note_id'],
            'author_uid': uid,
            'created_at': row['created_at'],
        })
    return list(peer_advisors_by_uid.values())


def get_peer_advising_note_template_usage(peer_advising_department_id):
    sql = """
        SELECT
          nt.id    AS id,
          nt.title AS title,
          COALESCE(COUNT(n.id), 0) AS usage_count
        FROM note_templates nt
        LEFT JOIN notes n
          ON n.note_template_id = nt.id
         AND n.deleted_at IS NULL
         AND n.peer_advising_department_id = nt.peer_advising_department_id
        WHERE nt.peer_advising_department_id = :peer_advising_department_id
          AND nt.deleted_at IS NULL
        GROUP BY nt.id, nt.title
        ORDER BY usage_count DESC, nt.title
    """

    def _to_api_json(row):
        return {
            'id': row['id'],
            'title': row['title'],
            'usageCount': row['usage_count'],
        }

    params = {'peer_advising_department_id': peer_advising_department_id}
    return [_to_api_json(row) for row in db.session.execute(text(sql), params).mappings()]



def get_total_peer_advising_notes(peer_advising_department_id=None):
    params = {}
    sql = f"""
      SELECT COUNT(*) AS count
      FROM notes
      WHERE
        peer_advising_department_id {'= :peer_advising_department_id' if peer_advising_department_id else 'IS NOT NULL'}
        AND deleted_at IS NULL
        AND is_draft IS FALSE
    """
    if peer_advising_department_id:
        params['peer_advising_department_id'] = peer_advising_department_id
    return next(row['count'] for row in db.session.execute(text(sql), params).mappings())
