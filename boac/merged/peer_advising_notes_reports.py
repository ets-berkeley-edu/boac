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


def get_peer_advising_note_author_count(peer_advising_department_id):
    query = """
      SELECT COUNT(DISTINCT au.uid) AS count
      FROM authorized_users au
      JOIN peer_advising_department_members pm ON pm.authorized_user_id = au.id
      JOIN notes n ON
        n.peer_advising_department_id = pm.peer_advising_department_id
        AND n.author_uid = au.uid
        AND n.deleted_at IS NULL
      WHERE
        pm.peer_advising_department_id = :peer_advising_department_id
    """
    results = db.session.execute(query, {'peer_advising_department_id': peer_advising_department_id})
    return [row['count'] for row in results][0]


def get_peer_advising_note_count_since(peer_advising_department_id, since_datetime=None):
    query = """
      SELECT COUNT(n.id) AS count
      FROM notes n
      WHERE
        n.peer_advising_department_id = :peer_advising_department_id
        AND n.deleted_at IS NULL
    """
    if since_datetime:
        query += f" AND n.created_at >= '{since_datetime.isoformat()}'"
    results = db.session.execute(query, {'peer_advising_department_id': peer_advising_department_id})
    return [row['count'] for row in results][0]


def get_notes_created_by_peer_advisors(
        peer_advising_department_id,
        from_created_at=None,
        to_created_at=None,
):
    query = f"""
        SELECT
          u.id as user_id,
          u.uid,
          n.id as note_id,
          n.author_name AS note_author_name,
          n.created_at as note_created_at
        FROM notes n
        JOIN authorized_users u ON u.uid = n.author_uid
        JOIN peer_advising_department_members m
          ON m.authorized_user_id = u.id AND m.role_type = 'peer_advisor' AND n.peer_advising_department_id = m.peer_advising_department_id
        WHERE
          n.peer_advising_department_id = :peer_advising_department_id
          AND n.deleted_at IS NULL
          {f" AND n.created_at >= '{from_created_at.isoformat()}'" if from_created_at else ''}
          {f" AND n.created_at <= '{to_created_at.isoformat()}'" if to_created_at else ''}
        GROUP BY u.id, u.uid, n.id, n.author_name, n.created_at
    """

    def _to_dict(row):
        return {
            'note_id': row['note_id'],
            'note_author_name': row['note_author_name'],
            'note_created_at': row['note_created_at'],
            'uid': row['uid'],
            'user_id': row['user_id'],
        }
    params = {'peer_advising_department_id': peer_advising_department_id}
    return [_to_dict(row) for row in db.session.execute(query, params)]


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


def get_total_peer_advising_notes(peer_advising_department_id):
    query = """
      SELECT COUNT(*) AS count
      FROM notes
      WHERE
        peer_advising_department_id = :peer_advising_department_id
        AND deleted_at IS NULL
        AND is_draft IS FALSE
    """
    results = db.session.execute(query, {'peer_advising_department_id': peer_advising_department_id})
    return [row['count'] for row in results][0]
