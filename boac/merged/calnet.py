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


from boac import std_commit
from boac.externals import calnet
from boac.models.json_cache import stow
from boac.models.student import Student


@stow('calnet_user_for_uid_{uid}')
def get_calnet_user_for_uid(app, uid):
    persons = calnet.client(app).search_uids([uid])
    p = persons[0] if len(persons) > 0 else None
    return {
        'uid': uid,
        'firstName': p and p['first_name'],
        'lastName': p and p['last_name'],
    }


def refresh_cohort_attributes(app, cohorts=None):
    students = cohorts or Student.query.all()
    # Students who play more than one sport will have multiple records.
    student_map = {}
    for student in students:
        student_map.setdefault(student.sid, []).append(student)
    csids = list(student_map.keys())

    # Search LDAP.
    all_attrs = calnet.client(app).search_csids(csids)
    if len(csids) != len(all_attrs):
        app.logger.warning(f'Looked for {len(csids)} CSIDS but only found {len(all_attrs)}')

    # Update the DB.
    for attrs in all_attrs:
        # Since we searched LDAP by CSID, we can be fairly sure that the results have CSIDs.
        csid = attrs['csid']
        name_split = attrs['sortable_name'].split(',') if 'sortable_name' in attrs else ''
        full_name = [name.strip() for name in reversed(name_split)]
        for student in student_map[csid]:
            student.uid = attrs['uid']
            # A manually-entered ASC name may be more nicely formatted than a student's CalNet default.
            # For now, don't overwrite it.
            student.first_name = student.first_name or (full_name[0] if len(full_name) else '')
            student.last_name = student.last_name or (full_name[1] if len(full_name) > 1 else '')
    return students


def fill_cohort_uids(app):
    to_update = Student.query.filter(Student.uid.is_(None)).all()
    refresh_cohort_attributes(app, to_update)
    std_commit()
    return to_update
