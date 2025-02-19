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

from datetime import datetime
import json
import random
import string

from boac import db, std_commit
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.util import utc_now
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from boac.models.json_cache import insert_row as insert_in_json_cache
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.topic import Topic
from boac.models.university_dept import UniversityDept
from boac.models.university_dept_member import UniversityDeptMember
# Models below are included so that db.create_all will find them.
from boac.models.alert import Alert # noqa
from boac.models.db_relationships import AlertView  # noqa
from boac.models.job_progress import JobProgress # noqa
from boac.models.json_cache import JsonCache # noqa
from flask import current_app as app
from sqlalchemy.sql import text

deleted_admin_uid = '44444'
deleted_user_uid = '33333'


def clear():
    with open(f"{app.config['BASE_DIR']}/scripts/db/drop_schema.sql", 'r') as ddlfile:
        ddltext = ddlfile.read()
    db.session().execute(text(ddltext))
    std_commit()


def load(load_test_data=False):
    _load_schemas()
    _load_users_and_departments()
    if load_test_data:
        _create_topics()
        _create_curated_groups()
        _create_cohorts()
    return db


def _load_schemas():
    """Create DB schema from SQL file."""
    with open(f"{app.config['BASE_DIR']}/scripts/db/schema.sql", 'r') as ddlfile:
        ddltext = ddlfile.read()
    db.session().execute(text(ddltext))
    std_commit()


def _load_users_and_departments():
    for code, name in BERKELEY_DEPT_CODE_TO_NAME.items():
        UniversityDept.create(code, name)
    _create_users()
    _create_department_memberships()
    _create_peer_advising_departments()


def _create_users():
    with open(f"{app.config['BASE_DIR']}/fixtures/development_db/test_users.json", 'r') as test_users_json:
        users = json.loads(test_users_json.read())
        for test_user in users:
            # This script can be run more than once. Do not create user if s/he exists in BOAC db.
            uid = test_user['uid']
            # Mock CSIDs and names are random unless we need them to correspond to test data elsewhere.
            csid = test_user['csid'] or datetime.now().strftime('%H%M%S%f')
            first_name = test_user.get('firstName', ''.join(random.choices(string.ascii_uppercase, k=6)))
            last_name = test_user.get('lastName', ''.join(random.choices(string.ascii_uppercase, k=6)))
            calnet_feed = {
                'uid': uid,
                'csid': csid,
                'firstName': first_name,
                'lastName': last_name,
                'name': f'{first_name} {last_name}',
            }
            if 'calnetDeptCodes' in test_user:
                calnet_feed['departments'] = []
                for dept_code in test_user['calnetDeptCodes']:
                    calnet_feed['departments'].append({
                        'deptCode': dept_code,
                        'deptName': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code),
                    })
            if 'title' in test_user:
                calnet_feed['title'] = test_user['title']
            insert_in_json_cache(f'calnet_user_for_uid_{uid}', calnet_feed)

            # Add user to authorized_users table if not already present.
            user = AuthorizedUser.find_by_uid(uid=uid)
            if not user:
                user = AuthorizedUser(
                    uid=uid,
                    created_by='0',
                    is_admin=test_user['isAdmin'],
                    in_demo_mode=test_user['inDemoMode'],
                    can_access_advising_data=test_user['canAccessAdvisingData'],
                    can_access_canvas_data=test_user['canAccessCanvasData'],
                    degree_progress_permission=test_user.get('degreeProgressPermission'),
                    search_history=test_user.get('searchHistory', []),
                )
                if test_user.get('deleted'):
                    user.deleted_at = utc_now()
                db.session.add(user)

        AuthorizedUser.delete(deleted_admin_uid)
        AuthorizedUser.delete(deleted_user_uid)

        std_commit(allow_test_environment=True)


def _create_department_memberships():
    with open(f"{app.config['BASE_DIR']}/fixtures/development_db/university_depts.json", 'r') as university_depts_json:
        university_depts = json.loads(university_depts_json.read())
        for dept_code, dept_membership in university_depts.items():
            university_dept = UniversityDept.find_by_dept_code(dept_code)
            db.session.add(university_dept)
            for user in dept_membership['users']:
                authorized_user = AuthorizedUser.find_by_uid(user['uid'])
                UniversityDeptMember.create_or_update_membership(
                    university_dept_id=university_dept.id,
                    authorized_user_id=authorized_user.id,
                    role=user['role'],
                    automate_membership=user['automate_membership'],
                )


def _create_peer_advising_departments():
    file_path = f"{app.config['BASE_DIR']}/fixtures/development_db/peer_advising_departments.json"
    with open(file_path, 'r') as peer_advising_departments_json:
        peer_advising_departments = json.loads(peer_advising_departments_json.read())
        for data in peer_advising_departments:
            peer_advising_department_name = data['peer_advising_department_name']
            university_dept = UniversityDept.find_by_dept_code(data['university_dept_code'])
            peer_advising_department = PeerAdvisingDepartment.create(
                name=peer_advising_department_name,
                university_dept_id=university_dept.id,
            )
            for user in data['users']:
                authorized_user = AuthorizedUser.find_by_uid(user['uid'])
                PeerAdvisingDepartmentMember.create_or_update_membership(
                    authorized_user_id=authorized_user.id,
                    peer_advising_department_id=peer_advising_department.id,
                    role_type=user['role'],
                )
                std_commit(allow_test_environment=True)


def _create_topics():
    Topic.create_topic('Other / Reason not listed')
    for index in range(10):
        topic = f'Topic for notes, {index}'
        Topic.create_topic(topic=topic)
    Topic.delete(Topic.create_topic('Topic for notes, deleted').id)
    std_commit(allow_test_environment=True)


def _create_curated_groups():
    asc_advisor = AuthorizedUser.find_by_uid('6446')
    CuratedGroup.create(asc_advisor.id, 'My Students')

    curated_group = CuratedGroup.create(asc_advisor.id, 'Four students')
    CuratedGroup.add_student(curated_group.id, '3456789012')
    CuratedGroup.add_student(curated_group.id, '5678901234')
    CuratedGroup.add_student(curated_group.id, '11667051')
    CuratedGroup.add_student(curated_group.id, '7890123456')

    coe_advisor = AuthorizedUser.find_by_uid('1133399')
    curated_group = CuratedGroup.create(coe_advisor.id, 'I have two students')
    CuratedGroup.add_student(curated_group.id, '7890123456')
    CuratedGroup.add_student(curated_group.id, '11667051')

    ce3_advisor = AuthorizedUser.find_by_uid('2525')
    curated_group = CuratedGroup.create(
        domain='admitted_students',
        name="My 'admitted_students' group",
        owner_id=ce3_advisor.id,
    )
    CuratedGroup.add_student(curated_group.id, '7890123456')
    std_commit(allow_test_environment=True)


def _create_cohorts():
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
        uid=coe_advisor_uid,
        name='Radioactive Women and Men',
        filter_criteria={
            'majors': ['Nuclear Engineering BS'],
        },
    )
    # The CE3 advisor will create a standard cohort and a cohort with domain='admitted_students'
    ce3_advisor_uid = '2525'
    CohortFilter.create(
        uid=ce3_advisor_uid,
        name='Undeclared students',
        filter_criteria={
            'majors': ['Undeclared'],
            'isInactiveAsc': False,
        },
    )
    CohortFilter.create(
        uid=ce3_advisor_uid,
        name='First Generation Students',
        filter_criteria={
            'isFirstGenerationCollege': True,
        },
        domain='admitted_students',
    )
    std_commit(allow_test_environment=True)


if __name__ == '__main__':
    import boac.factory
    boac.factory.create_app()
    load()
