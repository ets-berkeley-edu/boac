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
