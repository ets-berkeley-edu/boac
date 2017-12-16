import re

import boac.api.util as api_util
from boac.externals import canvas, sis_enrollments_api
from boac.lib.berkeley import sis_term_id_for_name
from flask import current_app as app


def merge_sis_enrollments(canvas_course_sites, cs_id, matriculation):
    courses_by_term = []

    def reverse_terms_until(stop_term):
        term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
        while True:
            yield term_name
            if (term_name == stop_term) or (term_name == app.config['CANVAS_EARLIEST_TERM']):
                break
            if term_name.startswith('Fall'):
                term_name = term_name.replace('Fall', 'Summer')
            elif term_name.startswith('Summer'):
                term_name = term_name.replace('Summer', 'Spring')
            elif term_name.startswith('Spring'):
                term_name = 'Fall ' + str(int(term_name[-4:]) - 1)

    for term_name in reverse_terms_until(matriculation):
        include_dropped_enrollments = (term_name == app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])
        merged_enrollments = merge_sis_enrollments_for_term(canvas_course_sites, cs_id, term_name, include_dropped_enrollments)
        if merged_enrollments and (len(merged_enrollments['enrollments']) or len(merged_enrollments['unmatchedCanvasSites'])):
            courses_by_term.append(merged_enrollments)
    return courses_by_term


def merge_sis_enrollments_for_term(canvas_course_sites, cs_id, term_name, include_dropped_enrollments=False):
    term_id = sis_term_id_for_name(term_name)
    enrollments = sis_enrollments_api.get_enrollments(cs_id, term_id)

    if enrollments:
        enrollments_by_class = {}
        term_section_ids = {}
        enrolled_units = 0
        for enrollment in enrollments.get('studentEnrollments', []):
            # Skip this class section if we've seen it already.
            section_id = enrollment.get('classSection').get('id')
            if section_id in term_section_ids:
                continue

            term_section_ids[section_id] = True
            section_feed = api_util.sis_enrollment_section_feed(enrollment)

            # The SIS enrollments API gives us no better unique identifier than the course display name.
            class_name = enrollment.get('classSection', {}).get('class', {}).get('course', {}).get('displayName')
            # If we haven't seen this class name before, we create a new feed entry for it.
            if class_name not in enrollments_by_class:
                enrollments_by_class[class_name] = api_util.sis_enrollment_class_feed(enrollment)
            # If we have seen this class name before, in most cases we'll just append the new section feed to the
            # existing class feed. However, because multiple concurrent primary-section enrollments aren't distinguished by
            # class name, we need to do an extra check for that case.
            # TODO In the rare case of multiple-primary enrollments with associated secondary sections, secondary section
            # handling will be unpredictable.
            else:
                if is_primary_section(section_feed):
                    existing_primary = next((sec for sec in enrollments_by_class[class_name]['sections'] if is_primary_section(sec)), None)
                    # If we do indeed have two primary sections under the same class name, disambiguate them.
                    if existing_primary:
                        # First, revise the existing class feed to include section number.
                        disambiguated_class_name = '{} {} {}'.format(class_name, existing_primary['component'], existing_primary['sectionNumber'])
                        enrollments_by_class[class_name]['displayName'] = disambiguated_class_name
                        enrollments_by_class[disambiguated_class_name] = enrollments_by_class[class_name]
                        del enrollments_by_class[class_name]
                        # Now create a new class feed, also with section number, for our new primary section.
                        class_name = '{} {} {}'.format(class_name, section_feed['component'], section_feed['sectionNumber'])
                        enrollments_by_class[class_name] = api_util.sis_enrollment_class_feed(enrollment)
                        enrollments_by_class[class_name]['displayName'] = class_name

            enrollments_by_class[class_name]['sections'].append(section_feed)
            if is_primary_section(section_feed):
                enrolled_units += section_feed['units']
                # Since we allow only one primary section per class, it's safe to associate units and grade information
                # with the class as well as the section.
                enrollments_by_class[class_name]['grade'] = section_feed['grade']
                enrollments_by_class[class_name]['gradingBasis'] = section_feed['gradingBasis']
                enrollments_by_class[class_name]['midtermGrade'] = section_feed['midtermGrade']
                enrollments_by_class[class_name]['units'] = section_feed['units']

        enrollments_feed = sorted(enrollments_by_class.values(), key=lambda x: x['displayName'])
        sort_sections(enrollments_feed)

        term_feed = {
            'termId': term_id,
            'termName': term_name,
            'enrollments': enrollments_feed,
            'enrolledUnits': enrolled_units,
            'unmatchedCanvasSites': [],
        }
    else:
        return

    for site in canvas_course_sites:
        merge_canvas_course_site(term_feed, site)

    # Screen out unwanted enrollments after course site merge so that associated sites are removed rather than orphaned.
    remove_athletic_enrollments(term_feed)
    # If dropped enrollments are to be included, collect section data in a separate list before removal.
    if include_dropped_enrollments:
        term_feed['droppedSections'] = collect_dropped_sections(term_feed)
    remove_dropped_enrollments(term_feed)

    sort_canvas_course_sites(term_feed)

    return term_feed


def collect_dropped_sections(term_feed):
    dropped_sections = []
    for enrollment in term_feed['enrollments']:
        for section in enrollment['sections']:
            if section['enrollmentStatus'] == 'D':
                dropped_sections.append({
                    'displayName': enrollment['displayName'],
                    'component': section['component'],
                    'sectionNumber': section['sectionNumber'],
                })
    return dropped_sections


def is_primary_section(section_feed):
    return section_feed['units'] > 0 and section_feed['enrollmentStatus'] == 'E'


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
        return (enrollment['displayName'].startswith('PHYSED 11')) or (enrollment['displayName'].startswith('PHYSED 12'))
    term_feed['enrollments'] = [enr for enr in term_feed['enrollments'] if not is_athletic_enrollment(enr)]


def remove_dropped_enrollments(term_feed):
    for enrollment in term_feed['enrollments']:
        enrollment['sections'] = [sec for sec in enrollment['sections'] if sec['enrollmentStatus'] != 'D']
    term_feed['enrollments'] = [enrollment for enrollment in term_feed['enrollments'] if len(enrollment['sections'])]


def sort_canvas_course_sites(term_feed):
    for enrollment in term_feed['enrollments']:
        enrollment['canvasSites'] = sorted(enrollment['canvasSites'], key=lambda x: x['canvasCourseId'])
    term_feed['unmatchedCanvasSites'] = sorted(term_feed['unmatchedCanvasSites'], key=lambda x: x['canvasCourseId'])


def sort_sections(enrollments_feed):
    # Sort by 1) enrollment status, 2) units descending, 3) section number.
    def section_key(sec):
        enrollment_status_keys = {
            'E': 0,
            'W': 1,
            'D': 2,
        }
        units_key = -1 * sec['units']
        return (
            enrollment_status_keys.get(sec['enrollmentStatus']),
            units_key,
            sec['sectionNumber'],
        )
    for enrollment in enrollments_feed:
        enrollment['sections'].sort(key=section_key)
