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

from bea.test_utils import utils
from boac import db, std_commit
from flask import current_app as app
from sqlalchemy import text


def get_boa_base_url():
    return app.config['BASE_URL']


# USERS

def get_user_login_count(user):
    sql = f"SELECT COUNT(uid) FROM user_logins WHERE uid = '#{user.uid}'"
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    return result['uid']


def create_admin_user(user):
    sql = f"""INSERT INTO authorized_users (created_at, updated_at, uid, is_admin, in_demo_mode,
                                            can_access_canvas_data, created_by, is_blocked)
              SELECT now(), now(), '#{user.uid}', true, false, true, '{utils.get_admin_uid()}', false
               WHERE NOT EXISTS (SELECT id FROM authorized_users WHERE uid = '#{user.uid}')"""
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
