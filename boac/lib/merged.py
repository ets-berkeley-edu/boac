import re

from boac import db
import boac.api.util as api_util
from boac.externals import calnet, canvas, sis_enrollments_api, sis_student_api
from boac.models.cohort import Cohort


def merge_sis_enrollments(canvas_course_sites, cs_id, term_id):
    # TODO For the moment, we're returning Canvas courses only for the current term as defined in
    # app config. Once we start grabbing multiple terms, we'll need additional sorting logic.
    enrollments = sis_enrollments_api.get_enrollments(cs_id, term_id)
    if enrollments:
        enrollments = enrollments.get('studentEnrollments', [])
    else:
        return

    for site in canvas_course_sites:
        site['sisEnrollments'] = []
        sections = canvas.get_course_sections(site['canvasCourseId'])
        if not sections:
            continue
        for section in sections:
            ccn_match = re.match(r'\ASEC:20\d{2}-[BCD]-(\d{5})\Z', section.get('sis_section_id'))
            if ccn_match:
                canvas_ccn = ccn_match.group(1)
            if not canvas_ccn:
                continue
            for enrollment in enrollments:
                sis_ccn = str(enrollment.get('classSection', {}).get('id'))
                if canvas_ccn == sis_ccn:
                    site['sisEnrollments'].append(api_util.sis_enrollment_api_feed(enrollment))
                    break


def merge_sis_profile(csid):
    sis_response = sis_student_api.get_student(csid)
    if not sis_response:
        return False

    sis_profile = {}
    merge_sis_profile_academic_status(sis_response, sis_profile)
    merge_sis_profile_degree_progress(sis_response, sis_profile)
    merge_sis_profile_emails(sis_response, sis_profile)
    merge_sis_profile_names(sis_response, sis_profile)
    merge_sis_profile_phones(sis_response, sis_profile)
    return sis_profile


def merge_sis_profile_academic_status(sis_response, sis_profile):
    for academic_status in sis_response.get('academicStatuses', []):
        sis_profile['cumulativeGPA'] = academic_status.get('cumulativeGPA', {}).get('average')
        sis_profile['level'] = academic_status.get('currentRegistration', {}).get('academicLevel', {}).get('level')

        for units in academic_status.get('cumulativeUnits', []):
            if units.get('type', {}).get('code') == 'Total':
                sis_profile['cumulativeUnits'] = units.get('unitsPassed')
                break

        try:
            student_plan = next(plan for plan in academic_status.get('studentPlans', []) if plan.get('primary'))
            plan = student_plan.get('academicPlan', {}).get('plan', {})
            sis_profile['plan'] = {
                'description': plan.get('description'),
                'fromDate': plan.get('fromDate'),
            }
        except StopIteration:
            pass


def merge_sis_profile_degree_progress(sis_response, sis_profile):
    sis_profile['degreeProgress'] = {
        'americanCultures': False,
        'americanInstitutions': False,
        'americanHistory': False,
        'entryLevelWriting': False,
        'foreignLanguage': False,
    }

    # TODO These code translations take provided descriptions at face value. Analysis and confirmation is needed.
    for attribute in sis_response.get('studentAttributes', []):
        code = attribute.get('type', {}).get('code')
        # American History completed at UCB
        if code == 'AHC':
            sis_profile['degreeProgress']['americanHistory'] = True
        # American History & Institutions high school or pre-matriculation
        elif code == 'AHI1' or code == 'AHIP':
            sis_profile['degreeProgress']['americanHistory'] = True
            sis_profile['degreeProgress']['americanInstitutions'] = True
        # American Institutions completed at UCB
        elif code == 'AIC':
            sis_profile['degreeProgress']['americanInstitutions'] = True
        # Entry-Level Writing satisfied pre-matriculation or completed at UCB
        elif code == 'ELW' or code == 'VELW':
            sis_profile['degreeProgress']['entryLevelWriting'] = True
        # American Cultures completed at UCB
        elif code == 'VAC':
            sis_profile['degreeProgress']['americanCultures'] = True
        # Foreign Language completed high school or at UCB
        elif code == 'VFLH' or code == 'VLFL':
            sis_profile['degreeProgress']['foreignLanguage'] = True


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


def refresh_cohort_attributes_from_calnet(app, cohorts=None):
    members = cohorts or Cohort.query.all()
    # Students who play more than one sport will have multiple cohort records.
    member_map = {}
    for m in members:
        member_map.setdefault(m.member_csid, []).append(m)
    csids = list(member_map.keys())

    # Search LDAP.
    all_attrs = calnet.client(app).search_csids(csids)
    if len(csids) != len(all_attrs):
        app.logger.warning('Looked for {} CSIDS but only found {}'.format(
            len(csids),
            len(all_attrs),
        ))

    # Update the DB.
    for attrs in all_attrs:
        # Since we searched LDAP by CSID, we can be fairly sure that the results have CSIDs.
        csid = attrs['csid']
        for m in member_map[csid]:
            m.member_uid = attrs['uid']
            # A manually-entered ASC name may be more nicely formatted than a student's CalNet default.
            # For now, don't overwrite it.
            m.member_name = m.member_name or attrs['sortable_name']
    return members


def fill_cohort_uids_from_calnet(app):
    to_update = Cohort.query.filter(Cohort.member_uid.is_(None)).all()
    refresh_cohort_attributes_from_calnet(app, to_update)
    db.session.commit()
    return to_update
