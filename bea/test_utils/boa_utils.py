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

from bea.models.degree_progress_perm import DegreeProgressPerm
from bea.models.department import Department
from bea.models.term import Term
from bea.models.user import User
from bea.test_utils import utils
from boac import db, std_commit
from flask import current_app as app
from sqlalchemy import text


def get_boa_base_url():
    return app.config['BASE_URL']


def get_term_code():
    return app.config['TERM_CODE']


def get_term_sis_id():
    return app.config['TERM_SIS_ID']


def get_current_term():
    return Term({
        'code': get_term_code(),
        'name': app.config['TERM_NAME'],
        'sis_id': get_term_sis_id(),
    })


def get_prev_term_sis_id(sis_id=None):
    current_sis_id = int(sis_id) if sis_id else int(app.config['TERM_SIS_ID'])
    previous_sis_id = current_sis_id - (4 if (current_sis_id % 10 == 2) else 3)
    return f'{previous_sis_id}'


# USERS

def get_user_login_count(user):
    sql = f"SELECT COUNT(uid) FROM user_logins WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    return result['count']


def create_admin_user(user):
    sql = f"""INSERT INTO authorized_users (created_at, updated_at, uid, is_admin, in_demo_mode,
                                            can_access_canvas_data, created_by, is_blocked)
              SELECT now(), now(), '{user.uid}', true, false, true, '{utils.get_admin_uid()}', false
               WHERE NOT EXISTS (SELECT id FROM authorized_users WHERE uid = '{user.uid}')"""
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def soft_delete_user(user):
    sql = f"UPDATE authorized_users SET deleted_at = NOW() WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def hard_delete_user(user):
    sql_1 = f"DELETE FROM authorized_users WHERE uid = '{user.uid}'"
    app.logger.info(sql_1)
    db.session.execute(text(sql_1))
    std_commit(allow_test_environment=True)
    sql_2 = f"DELETE FROM json_cache WHERE key = 'calnet_user_for_uid_' || '{user.uid}'"
    app.logger.info(sql_2)
    db.session.execute(text(sql_2))
    std_commit(allow_test_environment=True)


def restore_user(user):
    sql = f"UPDATE authorized_users SET deleted_at = NULL WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def get_dept_advisors(dept, membership=None):
    clause = ''
    # "Notes Only" isn't a real department, so it's a special case
    if dept == Department.NOTES_ONLY:
        if membership:
            role_code = membership.advisor_role.value['code']
            clause = f"AND university_dept_members.role = '{role_code}'"
        sql = f"""SELECT authorized_users.uid AS uid,
                         authorized_users.can_access_advising_data AS can_access_advising_data,
                         authorized_users.can_access_canvas_data AS can_access_canvas_data,
                         authorized_users.degree_progress_permission AS deg_prog_perm,
                         string_agg(ud.dept_code,',') AS depts
                    FROM authorized_users
                    JOIN university_dept_members
                      ON authorized_users.id = university_dept_members.authorized_user_id
                    JOIN university_depts ud
                      ON university_dept_members.university_dept_id = ud.id
                   WHERE authorized_users.deleted_at IS NULL
                     AND authorized_users.can_access_canvas_data IS FALSE
                        {clause}
                GROUP BY authorized_users.uid,
                         authorized_users.can_access_advising_data,
                         authorized_users.can_access_canvas_data,
                         authorized_users.degree_progress_permission"""
    else:
        if membership:
            role_code = membership.advisor_role.value['code']
            clause = f"AND udm1.role = '{role_code}'"
        sql = f"""SELECT authorized_users.uid AS uid,
                         authorized_users.can_access_advising_data AS can_access_advising_data,
                         authorized_users.can_access_canvas_data AS can_access_canvas_data,
                         authorized_users.degree_progress_permission AS deg_prog_perm,
                         string_agg(ud2.dept_code,',') AS depts
                    FROM authorized_users
                    JOIN university_dept_members udm1
                      ON authorized_users.id = udm1.authorized_user_id
                    JOIN university_depts ud1
                      ON udm1.university_dept_id = ud1.id
                     AND ud1.dept_code = '{dept.value['code']}'
                    JOIN university_dept_members udm2
                      ON authorized_users.id = udm2.authorized_user_id
                    JOIN university_depts ud2
                      ON udm2.university_dept_id = ud2.id
                   WHERE authorized_users.deleted_at IS NULL
                        {clause}
                GROUP BY authorized_users.uid,
                         authorized_users.can_access_advising_data,
                         authorized_users.can_access_canvas_data,
                         authorized_users.degree_progress_permission"""

    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    advisors = []
    for row in result:

        depts = []
        dept_memberships = []
        dept_codes = row['depts'].split(',')
        for dc in dept_codes:
            for dept in Department:
                if dept.value['code'] == dc:
                    depts.append(dept)
                    dept_memberships.append(dept)

        if row['deg_prog_perm'] == 'read':
            degree_progress_perm = DegreeProgressPerm.READ
        elif row['deg_prog_perm'] == 'read_write':
            degree_progress_perm = DegreeProgressPerm.WRITE
        else:
            degree_progress_perm = None

        user = User({
            'uid': row['uid'],
            'active': True,
            'can_access_advising_data': (True if row['can_access_advising_data'] == 't' else False),
            'can_access_canvas_data': (True if row['can_access_canvas_data'] == 't' else False),
            'degree_progress_perm': degree_progress_perm,
            'depts': depts,
            'dept_memberships': dept_memberships,
        })
        advisors.append(user)
    return advisors


def get_advisor_names(advisor):
    sql = f"""SELECT author_name,
                     created_at
                FROM notes
               WHERE author_uid = '{advisor.uid}'
            ORDER BY created_at DESC"""
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

    names = list(map(lambda n: n['author_name'], result))
    names = list(set(names))
    if names:
        advisor.full_name = names[0]
        advisor.alt_names = names[1::]

# NOTES


def get_sids_with_notes_of_src_boa(drafts=False):
    sql = f"""SELECT DISTINCT sid
                FROM notes
               WHERE body NOT LIKE '%QA Test%'
                 AND deleted_at IS NULL
                 AND is_private IS FALSE
                 AND is_draft IS {'TRUE' if drafts else 'FALSE'}"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return list(map(lambda r: r['sid'], results))
