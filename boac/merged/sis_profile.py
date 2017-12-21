import re
from boac.externals import sis_degree_progress_api
from boac.externals import sis_student_api
from boac.models.json_cache import stow
from boac.models.normalized_cache_student import NormalizedCacheStudent
from boac.models.normalized_cache_student_major import NormalizedCacheStudentMajor


@stow('merged_sis_profile_{csid}')
def merge_sis_profile(csid):
    sis_response = sis_student_api.get_student(csid)
    if not sis_response:
        return False

    sis_profile = {}
    merge_sis_profile_academic_status(sis_response, sis_profile)
    merge_sis_profile_emails(sis_response, sis_profile)
    merge_sis_profile_names(sis_response, sis_profile)
    merge_sis_profile_phones(sis_response, sis_profile)
    if sis_profile['academicCareer'] == 'UGRD':
        sis_profile['degreeProgress'] = sis_degree_progress_api.parsed_degree_progress(csid)

    store_normalized_profile(csid, sis_profile)

    return sis_profile


def merge_sis_profile_academic_status(sis_response, sis_profile):
    academic_statuses = sis_response.get('academicStatuses', [])
    if len(academic_statuses):
        academic_status = academic_statuses[0]
    else:
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

    sis_profile['plans'] = []
    for student_plan in academic_status.get('studentPlans', []):
        academic_plan = student_plan.get('academicPlan', {})
        # SIS majors come in five flavors.
        if academic_plan.get('type', {}).get('code') not in ['MAJ', 'SS', 'SP', 'HS', 'CRT']:
            continue
        plan = academic_plan.get('plan', {})
        plan_feed = {
            'description': plan.get('description'),
        }
        # Add program unless plan code indicates undeclared.
        if plan.get('code') != '25000U':
            program = student_plan.get('academicPlan', {}).get('academicProgram', {}).get('program', {})
            plan_feed['program'] = program.get('description')
        sis_profile['plans'].append(plan_feed)


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
            sis_profile['preferredName'] = name.get('formattedName')
        elif code == 'PRI':
            sis_profile['primaryName'] = name.get('formattedName')
        if 'primaryName' in sis_profile and 'preferredName' in sis_profile:
            break


def merge_sis_profile_phones(sis_response, sis_profile):
    phones_by_code = {
        phone.get('type', {}).get('code'): phone.get('number')
        for phone in sis_response.get('phones', [])
    }
    sis_profile['phoneNumber'] = phones_by_code.get('CELL') or phones_by_code.get('LOCL') or phones_by_code.get('HOME')


def store_normalized_profile(csid, sis_profile):
    gpa = sis_profile.get('cumulativeGPA')
    level = sis_profile.get('level', {}).get('description')
    units = sis_profile.get('cumulativeUnits')
    NormalizedCacheStudent.update_profile(csid, gpa=gpa, level=level, units=units)

    majors = [plan['description'] for plan in sis_profile.get('plans', [])]
    NormalizedCacheStudentMajor.update_majors(csid, majors)
