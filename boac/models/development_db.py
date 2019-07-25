"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

from datetime import datetime
import random
import string

from boac import db, std_commit
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, BERKELEY_DEPT_NAME_TO_CODE
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from boac.models.json_cache import insert_row as insert_in_json_cache
from boac.models.topic import Topic
from boac.models.university_dept import UniversityDept
# Models below are included so that db.create_all will find them.
from boac.models.alert import Alert # noqa
from boac.models.db_relationships import AlertView, cohort_filter_owners, UniversityDeptMember  # noqa
from boac.models.job_progress import JobProgress # noqa
from boac.models.json_cache import JsonCache # noqa
from flask import current_app as app
from sqlalchemy.sql import text


no_calnet_record_for_uid = '13'

_test_users = [
    [no_calnet_record_for_uid, None, True, False],  # This user has no entry in calnet_search_entries
    ['2040', None, True, True],
    ['53791', None, True, False],
    ['95509', None, True, False],
    ['177473', None, True, False],
    ['1133399', '800700600', False, False],
    ['211159', None, True, False],
    ['242881', '100100600', False, False, 'HENGL'],
    ['1022796', '100100300', False, False],
    ['1015674', None, False, False],
    ['1049291', None, True, False],
    ['1081940', '100200300', False, False],
    ['90412', '100100100', True, False],
    ['6446', None, False, False],
]

_university_depts = {
    'COENG': {
        'automate_memberships': True,
        'users': [
            {
                'uid': '1022796',
                'is_advisor': True,
                'is_director': False,
            },
            {
                'uid': '90412',
                'is_advisor': True,
                'is_director': False,
            },
            {
                'uid': '1133399',
                'is_advisor': True,
                'is_director': False,
            },
            {
                'uid': '13',
                'is_advisor': True,
                'is_director': False,
            },
        ],
    },
    'PHYSI': {
        'automate_memberships': False,
        'users': [
            {
                'uid': '53791',
                'is_advisor': False,
                'is_director': True,
            },
        ],
    },
    'QCADVMAJ': {
        'automate_memberships': True,
        'users': [
            {
                'uid': '242881',
                'is_advisor': True,
                'is_director': False,
            },
        ],
    },
    'UWASC': {
        'automate_memberships': False,
        'users': [
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
    },
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
        create_advising_note_topics()
        create_curated_groups()
        create_cohorts()
    return db


def load_schemas():
    """Create DB schema from SQL file."""
    with open(app.config['BASE_DIR'] + '/scripts/db/schema.sql', 'r') as ddlfile:
        ddltext = ddlfile.read()
    db.session().execute(text(ddltext))
    std_commit()


def load_development_data():
    for name, code in BERKELEY_DEPT_NAME_TO_CODE.items():
        UniversityDept.create(code, name, False)
    for test_user in _test_users:
        # This script can be run more than once. Do not create user if s/he exists in BOAC db.
        uid = test_user[0]
        csid = test_user[1]
        user = AuthorizedUser.find_by_uid(uid=uid)
        if uid != no_calnet_record_for_uid:
            # Put mock CalNet data in our json_cache for all users EXCEPT the test "no_calnet_record" user.
            first_name = ''.join(random.choices(string.ascii_uppercase, k=6))
            last_name = ''.join(random.choices(string.ascii_uppercase, k=6))
            calnet_feed = {
                'uid': uid,
                # Mock CSIDs are random unless we need them to correspond to test data elsewhere.
                'csid': csid or datetime.now().strftime('%H%M%S%f'),
                'firstName': first_name,
                'lastName': last_name,
                'name': f'{first_name} {last_name}',
            }
            if len(test_user) > 4:
                calnet_feed['departments'] = [
                    {
                        'code': test_user[4],
                        'name': BERKELEY_DEPT_CODE_TO_NAME.get(test_user[4]),
                    },
                ]
            insert_in_json_cache(f'calnet_user_for_uid_{uid}', calnet_feed)
        if not user:
            user = AuthorizedUser(uid=uid, is_admin=test_user[2], in_demo_mode=test_user[3])
            db.session.add(user)
    for dept_code, dept_membership in _university_depts.items():
        university_dept = UniversityDept.find_by_dept_code(dept_code)
        university_dept.automate_memberships = dept_membership['automate_memberships']
        db.session.add(university_dept)
        for user in dept_membership['users']:
            authorized_user = AuthorizedUser.find_by_uid(user['uid'])
            UniversityDeptMember.create_membership(
                university_dept,
                authorized_user,
                user['is_advisor'],
                user['is_director'],
            )
    std_commit(allow_test_environment=True)


def create_advising_note_topics():
    for i in range(5):
        Topic.create_topic(f'Topic {i}')
    delete_me = Topic.create_topic('I am a deleted topic')
    Topic.delete(delete_me.id)
    std_commit(allow_test_environment=True)


def create_curated_groups():
    admin_user = AuthorizedUser.find_by_uid('2040')
    CuratedGroup.create(admin_user.id, 'My Students')

    asc_advisor = AuthorizedUser.find_by_uid('6446')
    CuratedGroup.create(asc_advisor.id, 'My Students')

    curated_group = CuratedGroup.create(asc_advisor.id, 'Four students')
    CuratedGroup.add_student(curated_group.id, '3456789012')
    CuratedGroup.add_student(curated_group.id, '5678901234')
    CuratedGroup.add_student(curated_group.id, '11667051')
    CuratedGroup.add_student(curated_group.id, '7890123456')

    coe_advisor = AuthorizedUser.find_by_uid('1133399')
    curated_group = CuratedGroup.create(coe_advisor.id, 'I have one student')
    CuratedGroup.add_student(curated_group.id, '7890123456')
    std_commit(allow_test_environment=True)


def create_cohorts():
    # Oliver's cohorts
    CohortFilter.create(
        uid='2040',
        name='All sports',
        filter_criteria={
            'groupCodes': ['MFB-DL', 'WFH'],
        },
    )
    CohortFilter.create(
        uid='2040',
        name='Football, Defense',
        filter_criteria={
            'groupCodes': ['MFB-DB', 'MFB-DL'],
        },
    )
    CohortFilter.create(
        uid='2040',
        name='Field Hockey',
        filter_criteria={
            'groupCodes': ['WFH'],
        },
    )
    # Flint's cohorts
    asc_advisor_uid = '1081940'
    CohortFilter.create(
        uid=asc_advisor_uid,
        name='Defense Backs, Inactive',
        filter_criteria={
            'groupCodes': ['MFB-DB'],
            'isInactiveAsc': True,
        },
    )
    CohortFilter.create(
        uid=asc_advisor_uid,
        name='Defense Backs, Active',
        filter_criteria={
            'groupCodes': ['MFB-DB'],
            'isInactiveAsc': False,
        },
    )
    CohortFilter.create(
        uid=asc_advisor_uid,
        name='Defense Backs, All',
        filter_criteria={
            'groupCodes': ['MFB-DB'],
        },
    )
    CohortFilter.create(
        uid=asc_advisor_uid,
        name='Undeclared students',
        filter_criteria={
            'majors': ['Undeclared'],
            'isInactiveAsc': False,
        },
    )
    CohortFilter.create(
        uid=asc_advisor_uid,
        name='All sports',
        filter_criteria={
            'groupCodes': ['MFB-DL', 'WFH'],
            'isInactiveAsc': False,
        },
    )
    coe_advisor_uid = '1133399'
    CohortFilter.create(
        uid=coe_advisor_uid,
        name='Roberta\'s Students',
        filter_criteria={
            'coeAdvisorLdapUids': [coe_advisor_uid],
        },
    )
    CohortFilter.create(
        uid='1133399',
        name='Radioactive Women and Men',
        filter_criteria={
            'majors': ['Nuclear Engineering BS'],
        },
    )
    std_commit(allow_test_environment=True)


if __name__ == '__main__':
    import boac.factory
    boac.factory.create_app()
    load()
