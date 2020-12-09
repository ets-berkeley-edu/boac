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


import os
import sys

from boac import db
from boac.lib import scriptify
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


@scriptify.in_app
def main(app):
    from boac.models.authorized_user import AuthorizedUser

    connection = db.engine.connect()
    sql = """INSERT
        INTO university_depts (dept_code, dept_name, created_at, updated_at)
        VALUES ('UWASC', 'Athletic Study Center', now(), now())
    """
    connection.execute(text(sql))
    result = connection.execute(text('SELECT id FROM university_depts WHERE dept_code = \'UWASC\''))
    university_dept_id = result.fetchall()[0][0]

    print(f'[INFO] Inserted \'Athletic Study Center\' department in db (university_dept_id = {university_dept_id})')

    for user in AuthorizedUser.query.all():
        if user.is_advisor or user.is_director:
            sql = f"""INSERT
                INTO university_dept_members
                    (university_dept_id, authorized_user_id, is_advisor, is_director, created_at, updated_at)
                VALUES
                    ({university_dept_id}, {user.id}, {user.is_advisor}, {user.is_director}, now(), now())
            """
            connection.execute(text(sql))
            print(f'[INFO] User {user.uid} added to \'Athletic Study Center\' with is_advisor={user.is_advisor} and is_director={user.is_director}')
    connection.close()
    print('\nDone.\n')


main()
