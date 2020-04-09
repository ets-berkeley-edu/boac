"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.api.appointments_controller import _advisor_attrs_for_uid
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.util import utc_now
from boac.models.appointment import Appointment
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user_extension import DropInAdvisor
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from boac.models.json_cache import insert_row as insert_in_json_cache
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


delete_this_admin_uid = '44444'
delete_this_uid = '33333'
no_calnet_record_for_uid = '13'

_test_users = [
    {
        # This user has no entry in calnet_search_entries
        'uid': no_calnet_record_for_uid,
        'csid': None,
        'isAdmin': True,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '1',
        'csid': '111111111',
        'isAdmin': False,
        'inDemoMode': True,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': False,
    },
    {
        'uid': '2',
        'csid': '222222222',
        'isAdmin': False,
        'inDemoMode': True,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': False,
    },
    {
        # User deleted (see below)
        'uid': delete_this_uid,
        'csid': '333333333',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': False,
        'canAccessCanvasData': False,
    },
    {
        # User deleted (see below)
        'uid': delete_this_admin_uid,
        'csid': '444444444',
        'isAdmin': True,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': False,
    },
    {
        'uid': '2040',
        'csid': None,
        'isAdmin': True,
        'inDemoMode': True,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '53791',
        'csid': '53791',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
        'firstName': 'Milicent',
        'lastName': 'Balthazar',
    },
    {
        'uid': '19735',
        'csid': None,
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '188242',
        'csid': None,
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '95509',
        'csid': None,
        'isAdmin': True,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '177473',
        'csid': None,
        'isAdmin': True,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '1133397',
        'csid': 'None',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '1133399',
        'csid': '800700600',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
        'firstName': 'Joni',
        'lastName': 'Mitchell',
    },
    {
        'uid': '211159',
        'csid': None,
        'isAdmin': True,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '242881',
        'csid': '100100600',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
        'title': 'Harmless Drudge',
        'calnetDeptCodes': ['HENGL'],
    },
    {
        'uid': '1022796',
        'csid': '100100300',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '6972201',
        'csid': '100400900',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': False,
    },
    {
        'uid': '1015674',
        'csid': None,
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
        'deleted': True,
    },
    {
        'uid': '1049291',
        'csid': None,
        'isAdmin': True,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '1081940',
        'csid': '100200300',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
        'searchHistory': ['Moe', 'Larry', 'Curly'],
    },
    {
        'uid': '90412',
        'csid': '100100100',
        'firstName': 'COE Add',
        'lastName': 'Visor',
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': False,
        'canAccessCanvasData': True,
    },
    {
        'uid': '6446',
        'csid': None,
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
    },
    {
        'uid': '666',
        'csid': None,
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
        'deleted': True,
    },
    {
        'uid': '1024',
        'csid': None,
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
        'deleted': True,
    },
    {
        'uid': '2525',
        'csid': None,
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': True,
        'deleted': False,
    },
    {
        'uid': '3535',
        'csid': None,
        'isAdmin': False,
        'inDemoMode': False,
        'canAccessAdvisingData': True,
        'canAccessCanvasData': False,
        'deleted': False,
    },
]

_university_depts = {
    'COENG': {
        'users': [
            {
                'uid': '1022796',
                'role': 'advisor',
                'isDropInAdvisor': False,
                'automate_membership': True,
            },
            {
                'uid': '6972201',
                'role': 'scheduler',
                'isDropInAdvisor': False,
                'automate_membership': False,
            },
            {
                'uid': '90412',
                'role': 'advisor',
                'isDropInAdvisor': True,
                'automate_membership': True,
            },
            {
                'uid': '1133399',
                'role': 'advisor',
                'isDropInAdvisor': True,
                'automate_membership': True,
            },
            {
                'uid': '13',
                'role': 'advisor',
                'isDropInAdvisor': False,
                'automate_membership': True,
            },
        ],
    },
    'QCADV': {
        'users': [
            {
                'uid': '53791',
                'role': 'director',
                'isDropInAdvisor': True,
                'automate_membership': False,
            },
            {
                'uid': '188242',
                'role': 'advisor',
                'isDropInAdvisor': False,
                'automate_membership': False,
            },
            {
                'uid': '19735',
                'role': 'scheduler',
                'isDropInAdvisor': False,
                'automate_membership': False,
            },
        ],
    },
    'QCADVMAJ': {
        'users': [
            {
                'uid': '53791',
                'role': 'director',
                'isDropInAdvisor': True,
                'automate_membership': False,
            },
            {
                'uid': '242881',
                'role': 'advisor',
                'isDropInAdvisor': False,
                'automate_membership': True,
            },
            {
                'uid': '1133397',
                'role': 'advisor',
                'isDropInAdvisor': False,
                'automate_membership': True,
            },
        ],
    },
    'UWASC': {
        'users': [
            {
                'uid': '1081940',
                'role': 'advisor',
                'isDropInAdvisor': True,
                'automate_membership': False,
            },
            {
                'uid': '90412',
                'role': 'director',
                'isDropInAdvisor': False,
                'automate_membership': False,
            },
            {
                'uid': '6446',
                'role': 'director',
                'isDropInAdvisor': False,
                'automate_membership': False,
            },
        ],
    },
    'ZCEEE': {
        'users': [
            {
                'uid': '2525',
                'role': 'advisor',
                'isDropInAdvisor': False,
                'automate_membership': False,
            },
            {
                'uid': '3535',
                'role': 'scheduler',
                'isDropInAdvisor': False,
                'automate_membership': False,
            },
        ],
    },
    'ZZZZZ': {
        'users': [
            {
                'uid': '1',
                'role': 'advisor',
                'isDropInAdvisor': False,
                'automate_membership': True,
            },
        ],
    },
    'GUEST': {
        'users': [
            {
                'uid': '2',
                'role': 'advisor',
                'isDropInAdvisor': False,
                'automate_membership': False,
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
    _load_schemas()
    _load_users_and_departments()
    if cohort_test_data:
        _create_topics()
        _create_appointments()
        _create_curated_groups()
        _create_cohorts()
    return db


def _load_schemas():
    """Create DB schema from SQL file."""
    with open(app.config['BASE_DIR'] + '/scripts/db/schema.sql', 'r') as ddlfile:
        ddltext = ddlfile.read()
    db.session().execute(text(ddltext))
    std_commit()


def _load_users_and_departments():
    for code, name in BERKELEY_DEPT_CODE_TO_NAME.items():
        UniversityDept.create(code, name)
    _create_users()
    _create_department_memberships()


def _create_users():
    for test_user in _test_users:
        # This script can be run more than once. Do not create user if s/he exists in BOAC db.
        uid = test_user['uid']
        # Mock CSIDs and names are random unless we need them to correspond to test data elsewhere.
        csid = test_user['csid'] or datetime.now().strftime('%H%M%S%f')
        first_name = test_user.get('firstName', ''.join(random.choices(string.ascii_uppercase, k=6)))
        last_name = test_user.get('lastName', ''.join(random.choices(string.ascii_uppercase, k=6)))

        # Put mock CalNet data in our json_cache for all users EXCEPT the test "no_calnet_record" user.
        if uid != no_calnet_record_for_uid:
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
                        'code': dept_code,
                        'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code),
                    })
            if 'title' in test_user:
                calnet_feed['title'] = test_user['title']
            insert_in_json_cache(f'calnet_user_for_uid_{uid}', calnet_feed)

        # Add user to authorized_users table if not already present.
        user = AuthorizedUser.find_by_uid(uid=uid)
        if not user:
            user = AuthorizedUser(
                uid=uid,
                created_by='2040',
                is_admin=test_user['isAdmin'],
                in_demo_mode=test_user['inDemoMode'],
                can_access_advising_data=test_user['canAccessAdvisingData'],
                can_access_canvas_data=test_user['canAccessCanvasData'],
                search_history=test_user.get('searchHistory', []),
            )
            if test_user.get('deleted'):
                user.deleted_at = utc_now()
            db.session.add(user)

    AuthorizedUser.delete_and_block(delete_this_admin_uid)
    AuthorizedUser.delete_and_block(delete_this_uid)

    std_commit(allow_test_environment=True)


def _create_department_memberships():
    for dept_code, dept_membership in _university_depts.items():
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
            if user['isDropInAdvisor']:
                DropInAdvisor.create_or_update_membership(
                    dept_code=dept_code,
                    authorized_user_id=authorized_user.id,
                    is_available=True,
                )


def _create_appointments():
    _create_cancelled_appointments()
    _create_checked_in_appointments()
    _create_reserved_appointments()
    _create_waiting_appointments()


def _create_cancelled_appointments():
    coe_advisor_user_id = AuthorizedUser.get_id_per_uid('90412')
    scheduler_user_id = AuthorizedUser.get_id_per_uid('6972201')
    cancel_me = Appointment.create(
        appointment_type='Drop-in',
        created_by=coe_advisor_user_id,
        dept_code='COENG',
        details='We will cancel this appointment.',
        student_sid='7890123456',
        topics=['Whoops'],
    )
    Appointment.cancel(
        appointment_id=cancel_me.id,
        cancelled_by=scheduler_user_id,
        cancel_reason='Just because',
        cancel_reason_explained='I felt like it.',
    )


def _create_checked_in_appointments():
    coe_scheduler_user_id = AuthorizedUser.get_id_per_uid('6972201')
    coe_advisor_uid = '90412'
    coe_advisor_user_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
    l_s_director_uid = '53791'
    l_s_director_user_id = AuthorizedUser.get_id_per_uid(l_s_director_uid)

    check_me_in = Appointment.create(
        appointment_type='Drop-in',
        created_by=coe_scheduler_user_id,
        dept_code='COENG',
        details='Pick me, pick me!',
        student_sid='3456789012',
        topics=['Topic for appointments, 2'],
    )
    Appointment.check_in(
        appointment_id=check_me_in.id,
        advisor_attrs=_advisor_attrs_for_uid(coe_advisor_uid),
        checked_in_by=coe_advisor_user_id,
    )
    check_me_in = Appointment.create(
        appointment_type='Drop-in',
        created_by=coe_advisor_user_id,
        dept_code='COENG',
        details='Making appointments is da bomb.',
        student_sid='5678901234',
        topics=['Good Show'],
    )
    Appointment.check_in(
        appointment_id=check_me_in.id,
        advisor_attrs=_advisor_attrs_for_uid(coe_advisor_uid),
        checked_in_by=coe_advisor_user_id,
    )
    check_me_in = Appointment.create(
        appointment_type='Drop-in',
        created_by=coe_scheduler_user_id,
        dept_code='COENG',
        details='We will check in this inactive student.',
        student_sid='3141592653',
        topics=['Please check me in.'],
    )
    Appointment.check_in(
        appointment_id=check_me_in.id,
        checked_in_by=coe_advisor_user_id,
        advisor_attrs=_advisor_attrs_for_uid(coe_advisor_uid),
    )
    # L&S College Advising
    check_me_in = Appointment.create(
        appointment_type='Drop-in',
        created_by=l_s_director_user_id,
        dept_code='QCADV',
        details='It is not the length of life, but depth of life.',
        student_sid='11667051',
        topics=['Topic for appointments, 1'],
    )
    Appointment.check_in(
        appointment_id=check_me_in.id,
        advisor_attrs=_advisor_attrs_for_uid(l_s_director_uid),
        checked_in_by=l_s_director_user_id,
    )


def _create_reserved_appointments():
    coe_advisor_attrs = _advisor_attrs_for_uid('90412')
    reserve_me = Appointment.create(
        appointment_type='Drop-in',
        created_by=coe_advisor_attrs['id'],
        dept_code='COENG',
        details='I will reserve this appointment.',
        student_sid='7890123456',
        topics=['Whoops'],
    )
    Appointment.reserve(appointment_id=reserve_me.id, reserved_by=coe_advisor_attrs['id'], advisor_attrs=coe_advisor_attrs)


def _create_waiting_appointments():
    coe_advisor_user_id = AuthorizedUser.get_id_per_uid('90412')
    coe_scheduler_user_id = AuthorizedUser.get_id_per_uid('6972201')
    l_s_director_user_id = AuthorizedUser.get_id_per_uid('53791')
    Appointment.create(
        appointment_type='Drop-in',
        created_by=coe_scheduler_user_id,
        dept_code='COENG',
        details='Meet me at the crossroads.',
        student_sid='3456789012',
        topics=['Topic for appointments, 2'],
    )
    Appointment.create(
        appointment_type='Drop-in',
        created_by=coe_advisor_user_id,
        dept_code='COENG',
        details='Life is what happens while you\'re making appointments.',
        student_sid='5678901234',
        topics=['Good Show'],
    )
    # L&S College Advising
    Appointment.create(
        appointment_type='Drop-in',
        created_by=l_s_director_user_id,
        dept_code='QCADV',
        details='C-c-catch the wave!',
        student_sid='5678901234',
        topics=['Topic for appointments, 1', 'Good Show'],
    )
    Appointment.create(
        appointment_type='Drop-in',
        created_by=l_s_director_user_id,
        dept_code='QCADV',
        details='You be you.',
        student_sid='11667051',
        topics=['Topic for appointments, 1'],
    )


def _create_topics():
    Topic.create_topic(
        'Other / Reason not listed',
        available_in_notes=True,
        available_in_appointments=True,
    )
    for index in range(10):
        true_for_both = index in [1, 5, 7]
        available_in_appointments = true_for_both or index % 2 == 0
        available_in_notes = true_for_both or index % 3 == 0
        if true_for_both:
            topic = f'Topic for all, {index}'
        elif available_in_appointments:
            topic = f'Topic for appointments, {index}'
        else:
            topic = f'Topic for notes, {index}'
        Topic.create_topic(
            topic=topic,
            available_in_appointments=available_in_appointments,
            available_in_notes=available_in_notes,
        )
    Topic.delete(Topic.create_topic('Topic for all, deleted', available_in_appointments=True).id)
    Topic.delete(Topic.create_topic('Topic for appointments, deleted', available_in_appointments=True).id)
    Topic.delete(Topic.create_topic('Topic for notes, deleted', available_in_notes=True).id)
    std_commit(allow_test_environment=True)


def _create_curated_groups():
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


def _create_cohorts():
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
