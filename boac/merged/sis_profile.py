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


import re
from boac.externals import sis_degree_progress_api
from boac.externals import sis_student_api
from boac.lib.berkeley import degree_program_url_for_major, term_name_for_sis_id
from boac.lib.util import vacuum_whitespace
from boac.models.json_cache import stow
from flask import current_app as app


@stow('merged_sis_profile_{csid}')
def get_merged_sis_profile(csid):
    sis_response = sis_student_api.get_student(csid)
    if not sis_response:
        return False

    sis_profile = {}
    merge_sis_profile_academic_status(sis_response, sis_profile)
    merge_sis_profile_emails(sis_response, sis_profile)

    # We have encountered at least one malformed Hub Student Profile feed in which the top-level
    # 'names' key points to an embedded 'names' array rather than simply pointing to the array.
    # See BOAC-362 for details.
    try:
        merge_sis_profile_names(sis_response, sis_profile)
    except AttributeError as e:
        app.logger.error(f'Hub Student API returned malformed response for SID {csid}')
        app.logger.error(e)

    merge_sis_profile_phones(sis_response, sis_profile)
    if sis_profile['academicCareer'] == 'UGRD':
        sis_profile['degreeProgress'] = sis_degree_progress_api.parsed_degree_progress(csid)

    return sis_profile


def merge_sis_profile_academic_status(sis_response, sis_profile):
    # The Hub may return multiple academic statuses. We'll select the first status with a well-formed academic
    # career that is not a concurrent enrollment.
    academic_status = None
    for status in sis_response.get('academicStatuses', []):
        career_code = status.get('currentRegistration', {}).get('academicCareer', {}).get('code')
        if career_code and career_code != 'UCBX':
            academic_status = status
            break
    if not academic_status:
        return

    sis_profile['cumulativeGPA'] = academic_status.get('cumulativeGPA', {}).get('average')
    sis_profile['level'] = academic_status.get('currentRegistration', {}).get('academicLevel', {}).get('level')
    sis_profile['termsInAttendance'] = academic_status.get('termsInAttendance')
    sis_profile['academicCareer'] = academic_status.get('currentRegistration', {}).get('academicCareer', {}).get('code')

    matriculation_term_name = academic_status.get('studentCareer', {}).get('matriculation', {}).get('term', {}).get('name')
    if matriculation_term_name and re.match('\A2\d{3} (?:Spring|Summer|Fall)\Z', matriculation_term_name):
        # "2015 Fall" to "Fall 2015"
        sis_profile['matriculation'] = ' '.join(reversed(matriculation_term_name.split()))

    for units in academic_status.get('cumulativeUnits', []):
        if units.get('type', {}).get('code') == 'Total':
            sis_profile['cumulativeUnits'] = units.get('unitsCumulative')
            break

    merge_sis_profile_plans(academic_status, sis_profile)


def merge_sis_profile_emails(sis_response, sis_profile):
    primary_email = None
    campus_email = None
    for email in sis_response.get('emails', []):
        if email.get('primary'):
            primary_email = email.get('emailAddress')
            break
        elif email.get('type', {}).get('code') == 'CAMP':
            campus_email = email.get('emailAddress')
    sis_profile['emailAddress'] = primary_email or campus_email


def merge_sis_profile_names(sis_response, sis_profile):
    for name in sis_response.get('names', []):
        code = name.get('type', {}).get('code')
        if code == 'PRF':
            sis_profile['preferredName'] = vacuum_whitespace(name.get('formattedName'))
        elif code == 'PRI':
            sis_profile['primaryName'] = vacuum_whitespace(name.get('formattedName'))
        if 'primaryName' in sis_profile and 'preferredName' in sis_profile:
            break


def merge_sis_profile_phones(sis_response, sis_profile):
    phones_by_code = {
        phone.get('type', {}).get('code'): phone.get('number')
        for phone in sis_response.get('phones', [])
    }
    sis_profile['phoneNumber'] = phones_by_code.get('CELL') or phones_by_code.get('LOCL') or phones_by_code.get('HOME')


def merge_sis_profile_plans(academic_status, sis_profile):
    sis_profile['plans'] = []
    for student_plan in academic_status.get('studentPlans', []):
        academic_plan = student_plan.get('academicPlan', {})
        # SIS majors come in five flavors.
        if academic_plan.get('type', {}).get('code') not in ['MAJ', 'SS', 'SP', 'HS', 'CRT']:
            continue
        plan = academic_plan.get('plan', {})
        major = plan.get('description')
        plan_feed = {
            'degreeProgramUrl': degree_program_url_for_major(major),
            'description': major,
        }
        # Find the latest expected graduation term from any plan.
        expected_graduation_term = student_plan.get('expectedGraduationTerm', {}).get('id')
        if expected_graduation_term and expected_graduation_term > sis_profile.get('expectedGraduationTerm', {}).get('id', '0'):
            sis_profile['expectedGraduationTerm'] = {
                'id': expected_graduation_term,
                'name': term_name_for_sis_id(expected_graduation_term),
            }
        # Add program unless plan code indicates undeclared.
        if plan.get('code') != '25000U':
            program = student_plan.get('academicPlan', {}).get('academicProgram', {}).get('program', {})
            plan_feed['program'] = program.get('description')
        sis_profile['plans'].append(plan_feed)
