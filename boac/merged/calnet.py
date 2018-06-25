"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac import db, std_commit
from boac.externals import calnet
from boac.models.json_cache import stow
from boac.models.student import Student
from flask import current_app as app


@stow('calnet_user_for_uid_{uid}')
def get_calnet_user_for_uid(app, uid):
    persons = calnet.client(app).search_uids([uid])
    p = persons[0] if len(persons) > 0 else None
    return {
        'uid': uid,
        'firstName': p and p['first_name'],
        'lastName': p and p['last_name'],
    }


def update_student_attributes(students=None):
    sid_map = {}
    for student in students:
        sid_map.setdefault(student.sid, []).append(student)
    sids = list(sid_map.keys())

    # Search LDAP.
    all_attributes = calnet.client(app).search_csids(sids)
    if len(sids) != len(all_attributes):
        ldap_sids = [l['csid'] for l in all_attributes]
        missing = set(sids) - set(ldap_sids)
        app.logger.warning(f'Looked for {len(sids)} SIDs but only found {len(all_attributes)} : missing {missing}')

    # Update db
    for a in all_attributes:
        # Since we searched LDAP by SID, we can be fairly sure that the results have SIDs.
        sid = a['csid']
        name_split = a['sortable_name'].split(',') if 'sortable_name' in a else ''
        full_name = [name.strip() for name in reversed(name_split)]
        for m in sid_map[sid]:
            new_uid = a['uid']
            if m.uid != new_uid:
                app.logger.info(f'For SID {sid}, changing UID {m.uid} to {new_uid}')
                m.uid = new_uid
            new_first_name = full_name[0] if len(full_name) else ''
            new_last_name = full_name[1] if len(full_name) > 1 else ''
            if (m.first_name != new_first_name) or (m.last_name != new_last_name):
                app.logger.info(f'For SID {sid}, changing name "{m.first_name} {m.last_name}" to "{new_first_name} {new_last_name}"')
                m.first_name = new_first_name
                m.last_name = new_last_name
    return students


def merge_student_calnet_data():
    students = Student.query.all()
    update_student_attributes(students)
    app.logger.info(f'Modified {len(db.session.dirty)} student records from calnet')
    std_commit()
