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

import csv
import os
import sys

from boac.lib import scriptify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


@scriptify.in_app
def main(app):
    from boac.models.authorized_user import AuthorizedUser
    from boac.models.student_group import StudentGroup
    from boac.models.student import Student

    advisor_watchlists_data = '/tmp/advisor_watchlists.csv'
    if os.path.isfile(advisor_watchlists_data):
        with open(advisor_watchlists_data) as csv_file:
            rows = csv.reader(csv_file)
            # Skip first row
            next(rows, None)
            for row in rows:
                if len(row) == 2:
                    owner_uid = row[0]
                    sid = row[1]
                    owner = AuthorizedUser.find_by_uid(owner_uid)
                    if owner:
                        if Student.find_by_sid(sid):
                            group = StudentGroup.get_or_create_my_primary(owner.id)
                            StudentGroup.add_student(group.id, sid)
                            print(f'[INFO] Student {sid} added to the \'My Students\' group owned by UID {owner.uid}')
                        else:
                            print(f'[WARN] Student {sid} does not exist')
                    else:
                        print(f'[WARN] AuthorizedUser {owner_uid} does not exist')
    else:
        print(f'[ERROR] File not found: {advisor_watchlists_data}')
    print('\nDone. Enjoy the rest of your day.\n')


main()
