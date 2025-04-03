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

from boac import db
from boac.externals.data_loch import get_basic_student_data
from boac.lib.util import to_iso_format
from boac.models.peer_advising_department import PeerAdvisingDepartment


def get_peer_advising_department_note_counts():
    query = """
      SELECT ud.dept_name, ud.dept_code, COUNT(*) AS count
        FROM peer_advising_departments pd
        JOIN university_depts ud ON pd.university_dept_id = ud.id
        JOIN notes n ON n.peer_advising_department_id = pd.id
       WHERE n.deleted_at IS NULL
         AND n.is_draft IS FALSE
       GROUP BY ud.dept_name, ud.dept_code
    """
    return [row for row in db.session.execute(query)]


def get_peer_advising_note_author_count(peer_advising_department_id=None):
    query = f"""
        SELECT COUNT(DISTINCT au.uid) AS count
        FROM authorized_users au
        JOIN peer_advising_department_members pm ON pm.authorized_user_id = au.id
        JOIN notes n ON
            n.peer_advising_department_id = pm.peer_advising_department_id
            AND n.author_uid = au.uid
            AND n.deleted_at IS NULL
        WHERE TRUE
            {'AND pm.peer_advising_department_id = :peer_advising_department_id' if peer_advising_department_id else ''}
    """
    results = db.session.execute(query, {'peer_advising_department_id': peer_advising_department_id})
    return [row['count'] for row in results][0]


def get_peer_advising_note_count_since(peer_advising_department_id, timeframe_month=None):
    query = f"""
      SELECT COUNT(n.id) AS count
      FROM notes n
      WHERE
        n.peer_advising_department_id = :peer_advising_department_id
        AND n.deleted_at IS NULL
        {f" AND to_char(n.created_at, 'YYYY-MM') = '{timeframe_month}'" if timeframe_month else ''}
    """
    results = db.session.execute(query, {'peer_advising_department_id': peer_advising_department_id})
    return [row['count'] for row in results][0]


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
        for row in db.session.execute(sql, {'peer_advising_department_id': peer_advising_department_id}):
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
    query = f"""
        SELECT
          n.id,
          n.author_name,
          n.author_uid,
          n.created_at
        FROM notes n
        WHERE
          n.peer_advising_department_id = :peer_advising_department_id
          AND n.deleted_at IS NULL
          {f" AND to_char(n.created_at, 'YYYY-MM') = '{timeframe_month}'" if timeframe_month else ''}
        ORDER BY n.author_name
    """
    return [row for row in db.session.execute(query, {'peer_advising_department_id': peer_advising_department_id})]


def get_peer_advising_note_template_usage(peer_advising_department_id):
    query = """
        SELECT DISTINCT(nt.id), nt.title, COUNT(DISTINCT nt.id) AS count
        FROM note_templates nt
        WHERE
          nt.peer_advising_department_id = :peer_advising_department_id
          AND nt.deleted_at IS NULL
        GROUP BY nt.id
        ORDER BY count DESC, nt.title
    """
    results = db.session.execute(query, {'peer_advising_department_id': peer_advising_department_id})

    def _to_api_json(row):
        return {
            'templateId': row['id'],
            'templateTitle': row['title'],
            'noteTemplateUsageCount': row['count'],
        }
    return [_to_api_json(row) for row in results]


def get_total_peer_advising_notes(peer_advising_department_id=None):
    params = {}
    query = f"""
      SELECT COUNT(*) AS count
      FROM notes
      WHERE
        peer_advising_department_id {'= :peer_advising_department_id' if peer_advising_department_id else 'IS NOT NULL'}
        AND deleted_at IS NULL
        AND is_draft IS FALSE
    """
    if peer_advising_department_id:
        params['peer_advising_department_id'] = peer_advising_department_id
    results = db.session.execute(query, params)
    return [row['count'] for row in results][0]
