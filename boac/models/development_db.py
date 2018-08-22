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
from boac.lib.berkeley import BERKELEY_DEPT_NAME_TO_CODE
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_cohort import CuratedCohort
from boac.models.university_dept import UniversityDept
# Models below are included so that db.create_all will find them.
from boac.models.alert import Alert # noqa
from boac.models.db_relationships import AlertView, cohort_filter_owners, UniversityDeptMember  # noqa
from boac.models.job_progress import JobProgress # noqa
from boac.models.json_cache import JsonCache # noqa
from flask import current_app as app
from sqlalchemy.sql import text


_test_users = [
    ['2040', True],
    ['53791', True],
    ['95509', True],
    ['177473', True],
    ['1133399', False],
    ['211159', True],
    ['242881', True],
    ['1022796', False],
    ['1015674', False],
    ['1049291', True],
    ['1081940', False],
    ['90412', True],
    ['6446', False],
]

_users_per_dept = {
    'COENG': [
        {
            'uid': '1022796',
            'is_advisor': False,
            'is_director': True,
        },
        {
            'uid': '90412',
            'is_advisor': True,
            'is_director': True,
        },
        {
            'uid': '1133399',
            'is_advisor': True,
            'is_director': False,
        },
    ],
    'UWASC': [
        {
            'uid': '1081940',
            'is_advisor': True,
            'is_director': False,
        },
        {
            'uid': '90412',
            'is_advisor': False,
            'is_director': True,
        },
        {
            'uid': '6446',
            'is_advisor': True,
            'is_director': True,
        },
    ],
}


def clear():
    with open(app.config['BASE_DIR'] + '/scripts/db/drop_schema.sql', 'r') as ddlfile:
        ddltext = ddlfile.read()
    db.session().execute(text(ddltext))
    std_commit()


def load(cohort_test_data=False):
    load_schemas()
    load_development_data()
    if cohort_test_data:
        create_curated_cohorts()
        create_filtered_cohorts()
    return db


def load_schemas():
    """Create DB schema from SQL file."""
    with open(app.config['BASE_DIR'] + '/scripts/db/schema.sql', 'r') as ddlfile:
        ddltext = ddlfile.read()
    db.session().execute(text(ddltext))
    std_commit()


def load_development_data():
    for name, code in BERKELEY_DEPT_NAME_TO_CODE.items():
        UniversityDept.create(code, name)
    for test_user in _test_users:
        # This script can be run more than once. Do not create user if s/he exists in BOAC db.
        user = AuthorizedUser.find_by_uid(uid=test_user[0])
        if not user:
            user = AuthorizedUser(uid=test_user[0], is_admin=test_user[1])
            db.session.add(user)
    for dept_code, users in _users_per_dept.items():
        university_dept = UniversityDept.find_by_dept_code(dept_code)
        for user in users:
            authorized_user = AuthorizedUser.find_by_uid(user['uid'])
            UniversityDeptMember.create_membership(
                university_dept,
                authorized_user,
                user['is_advisor'],
                user['is_director'],
            )
    std_commit(allow_test_environment=True)


def create_curated_cohorts():
    admin_id = AuthorizedUser.find_by_uid('2040').id
    CuratedCohort.create(admin_id, 'My Students')

    advisor_id = AuthorizedUser.find_by_uid('6446').id
    CuratedCohort.create(advisor_id, 'My Students')
    curated_cohort = CuratedCohort.create(advisor_id, 'Cool Kids')
    CuratedCohort.add_student(curated_cohort.id, '3456789012')  # PaulK
    CuratedCohort.add_student(curated_cohort.id, '5678901234')  # Sandeep
    CuratedCohort.add_student(curated_cohort.id, '11667051')    # Deborah
    CuratedCohort.add_student(curated_cohort.id, '7890123456')  # PaulF

    coe_advisor = AuthorizedUser.find_by_uid('1133399')
    curated_cohort = CuratedCohort.create(coe_advisor.id, 'Cohort of One')
    CuratedCohort.add_student(curated_cohort.id, '7890123456')  # PaulF

    std_commit(allow_test_environment=True)


def create_filtered_cohorts():
    # Oliver's cohorts
    CohortFilter.create(uid='2040', label='All sports', group_codes=['MFB-DL', 'WFH'])
    CohortFilter.create(uid='2040', label='Football, Defense', group_codes=['MFB-DB', 'MFB-DL'])
    CohortFilter.create(uid='2040', label='Field Hockey', group_codes=['WFH'])
    # Flint's cohorts
    asc_advisor_uid = '1081940'
    CohortFilter.create(uid=asc_advisor_uid, label='Defense Backs, Inactive', group_codes=['MFB-DB'], is_inactive_asc=True)
    CohortFilter.create(uid=asc_advisor_uid, label='Defense Backs, Active', group_codes=['MFB-DB'], is_inactive_asc=False)
    CohortFilter.create(uid=asc_advisor_uid, label='Defense Backs, All', group_codes=['MFB-DB'])
    CohortFilter.create(uid=asc_advisor_uid, label='Undeclared students', majors=['Undeclared'], is_inactive_asc=False)
    CohortFilter.create(uid=asc_advisor_uid, label='All sports', group_codes=['MFB-DL', 'WFH'], is_inactive_asc=False)
    # Sandeep's cohorts
    coe_advisor_uid = '1133399'
    CohortFilter.create(uid=coe_advisor_uid, label='Sandeep\'s Students', advisor_ldap_uids=[coe_advisor_uid])
    CohortFilter.create(uid='1133399', label='Radioactive Women and Men', majors=['Nuclear Engineering BS'])
    std_commit(allow_test_environment=True)


if __name__ == '__main__':
    import boac.factory
    boac.factory.create_app()
    load()
