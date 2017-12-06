import re

from boac import db
import boac.api.util as api_util
from boac.externals import calnet, canvas, sis_enrollments_api, sis_student_api
from boac.lib.berkeley import sis_term_id_for_name
from boac.models.team_member import TeamMember
from flask import current_app as app


def merge_sis_enrollments(canvas_course_sites, cs_id, matriculation):
    courses_by_term = []

    def reverse_terms_until(stop_term):
        term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
        while True:
            yield term_name
            if (term_name == stop_term) or not stop_term:
                break
            if term_name.startswith('Fall'):
                term_name = term_name.replace('Fall', 'Summer')
            elif term_name.startswith('Summer'):
                term_name = term_name.replace('Summer', 'Spring')
            elif term_name.startswith('Spring'):
                term_name = 'Fall ' + str(int(term_name[-4:]) - 1)

    for term_name in reverse_terms_until(matriculation):
        merged_enrollments = merge_sis_enrollments_for_term(canvas_course_sites, cs_id, term_name)
        if merged_enrollments and (len(merged_enrollments['enrollments']) or len(merged_enrollments['unmatchedCanvasSites'])):
            courses_by_term.append(merged_enrollments)
    return courses_by_term


def merge_sis_enrollments_for_term(canvas_course_sites, cs_id, term_name):
    term_id = sis_term_id_for_name(term_name)
    enrollments = sis_enrollments_api.get_enrollments(cs_id, term_id)

    if enrollments:
        enrollments_by_class = {}
        term_section_ids = {}
        for enrollment in enrollments.get('studentEnrollments', []):
            # Skip this class section if we've seen it already.
            section_id = enrollment.get('classSection').get('id')
            if section_id in term_section_ids:
                continue
            else:
                term_section_ids[section_id] = True
            # SIS class id (as distinct from section id or course id) is not surfaced by the SIS enrollments API. Our best
            # unique identifier is the class display name.
            class_name = enrollment.get('classSection', {}).get('class', {}).get('displayName')
            if class_name not in enrollments_by_class:
                enrollments_by_class[class_name] = api_util.sis_enrollment_class_feed(enrollment)
            enrollments_by_class[class_name]['sections'].append(api_util.sis_enrollment_section_feed(enrollment))
        enrollments_feed = enrollments_by_class.values()

        term_feed = {
            'termId': term_id,
            'termName': term_name,
            'enrollments': enrollments_feed,
            'unmatchedCanvasSites': [],
        }
    else:
        return

    for site in canvas_course_sites:
        merge_canvas_course_site(term_feed, site)

    # Screen out unwanted enrollments after course site merge so that associated sites are removed rather than orphaned.
    remove_athletic_enrollments(term_feed)
    if term_name != app.config['CANVAS_CURRENT_ENROLLMENT_TERM']:
        remove_dropped_enrollments(term_feed)

    return term_feed


def merge_canvas_course_site(term_feed, site):
    if site['courseTerm'] != term_feed['termName']:
        return
    site_matched = False
    sections = canvas.get_course_sections(site['canvasCourseId'], term_feed['termId'])
    if not sections:
        return
    for section in sections:
        # Manually created site sections will have no integration ID.
        canvas_sis_section_id = section.get('sis_section_id') or ''
        ccn_match = re.match(r'\ASEC:20\d{2}-[BCD]-(\d{5})', canvas_sis_section_id)
        if not ccn_match:
            continue
        canvas_ccn = ccn_match.group(1)
        if not canvas_ccn:
            continue
        for enrollment in term_feed['enrollments']:
            matching_section = next((section for section in enrollment['sections'] if canvas_ccn == str(section.get('ccn'))), None)
            if matching_section:
                site_matched = True
                enrollment['canvasSites'].append(site)
                break
        if site_matched:
            break
    if not site_matched:
        term_feed['unmatchedCanvasSites'].append(site)


def remove_athletic_enrollments(term_feed):
    def is_athletic_enrollment(enrollment):
        return (enrollment['displayName'] == 'PHYSED 11') or (enrollment['displayName'] == 'PHYSED 12')
    term_feed['enrollments'] = [enr for enr in term_feed['enrollments'] if not is_athletic_enrollment(enr)]


def remove_dropped_enrollments(term_feed):
    def is_dropped(enrollment):
        for section in enrollment['sections']:
            if section['enrollmentStatus'] != 'D':
                return False
        return True
    term_feed['enrollments'] = [enr for enr in term_feed['enrollments'] if not is_dropped(enr)]


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
    academic_statuses = sis_response.get('academicStatuses', [])
    if len(academic_statuses):
        academic_status = academic_statuses[0]
    else:
        return

    sis_profile['cumulativeGPA'] = academic_status.get('cumulativeGPA', {}).get('average')
    sis_profile['level'] = academic_status.get('currentRegistration', {}).get('academicLevel', {}).get('level')

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
        if academic_plan.get('type', {}).get('code') != 'MAJ':
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
    members = cohorts or TeamMember.query.all()
    # Students who play more than one sport will have multiple records.
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
    to_update = TeamMember.query.filter(TeamMember.member_uid.is_(None)).all()
    refresh_cohort_attributes_from_calnet(app, to_update)
    db.session.commit()
    return to_update
