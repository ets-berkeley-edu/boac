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


import boac.api.util as api_util
from boac.externals import data_loch, sis_enrollments_api
from boac.lib.berkeley import sis_term_id_for_name
from boac.models.alert import Alert
from boac.models.json_cache import stow
from boac.models.normalized_cache_enrollment import NormalizedCacheEnrollment
from flask import current_app as app


def merge_sis_enrollments(canvas_course_sites, uid, cs_id, matriculation):
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
        merged_enrollments = merge_sis_enrollments_for_term(canvas_course_sites, uid, cs_id, term_name)
        if merged_enrollments and (len(merged_enrollments['enrollments']) or len(merged_enrollments['unmatchedCanvasSites'])):
            courses_by_term.append(merged_enrollments)
    return courses_by_term


def merge_sis_enrollments_for_term(canvas_course_sites, uid, cs_id, term_name):
    term_id = sis_term_id_for_name(term_name)
    enrollments = data_loch.get_sis_enrollments(uid, term_id) or []
    term_feed = merge_enrollment(cs_id, enrollments, term_id, term_name)

    for site in canvas_course_sites:
        merge_canvas_course_site(term_feed, site)

    # Screen out unwanted enrollments after course site merge so that associated sites are removed rather than orphaned.
    remove_athletic_enrollments(term_feed)

    sort_canvas_course_sites(term_feed)

    return term_feed


def merge_drops_and_midterms(cs_id, term_name, term_feed):
    """Check for dropped classes and midterm deficient grades, creating new Alerts as needed."""
    if term_name != app.config['CANVAS_CURRENT_ENROLLMENT_TERM']:
        return term_feed

    term_id = sis_term_id_for_name(term_name)
    drops_and_midterms = sis_enrollments_api.get_drops_and_midterms(cs_id, term_id) or {}
    term_feed['droppedSections'] = drops_and_midterms.get('droppedPrimarySections', [])
    section_midterms = drops_and_midterms.get('midtermGrades', {})
    for enrollment in term_feed['enrollments']:
        for section in enrollment['sections']:
            section_id = section['ccn']
            if section_id in section_midterms:
                midterm_grade = section_midterms[section_id]
                section['midtermGrade'] = midterm_grade
                enrollment['midtermGrade'] = midterm_grade
                Alert.update_midterm_grade_alerts(cs_id, term_id, section_id, enrollment['displayName'], midterm_grade)
    return term_feed


@stow('merged_enrollment_{cs_id}', for_term=True)
def merge_enrollment(cs_id, enrollments, term_id, term_name):
    enrollments_by_class = {}
    term_section_ids = {}
    enrolled_units = 0
    for enrollment in enrollments:
        # Skip this class section if we've seen it already.
        section_id = enrollment.get('sis_section_id')
        if section_id in term_section_ids:
            continue

        term_section_ids[section_id] = True
        section_feed = {
            'ccn': enrollment['sis_section_id'],
            'component': enrollment['sis_instruction_format'],
            'sectionNumber': enrollment['sis_section_num'],
            'enrollmentStatus': enrollment['sis_enrollment_status'],
            'units': enrollment['units'],
            'gradingBasis': api_util.translate_grading_basis(enrollment['grading_basis']),
            'grade': enrollment['grade'],
            'primary': enrollment['sis_primary'],
        }

        # The SIS enrollments API gives us no better unique identifier than the course display name.
        class_name = enrollment['sis_course_name']
        # If we haven't seen this class name before, we create a new feed entry for it.
        if class_name not in enrollments_by_class:
            enrollments_by_class[class_name] = api_util.sis_enrollment_class_feed(enrollment)

        if is_enrolled_primary_section(section_feed):
            class_name = check_for_multiple_primary_sections(enrollment, class_name, enrollments_by_class, section_feed)

        enrollments_by_class[class_name]['sections'].append(section_feed)
        if is_enrolled_primary_section(section_feed):
            enrolled_units += section_feed['units']
        # Since only one enrolled primary section is allowed per class, it's safe to associate units and grade
        # information with the class as well as the section. If a primary section is waitlisted, do the same
        # association unless we've already done it with a different section (this case may not arise in practice).
        if is_enrolled_primary_section(section_feed) or (
                section_feed['primary'] and 'units' not in enrollments_by_class[class_name]):
            enrollments_by_class[class_name]['grade'] = section_feed['grade']
            enrollments_by_class[class_name]['gradingBasis'] = section_feed['gradingBasis']
            enrollments_by_class[class_name]['units'] = section_feed['units']

    enrollments_feed = sorted(enrollments_by_class.values(), key=lambda x: x['displayName'])
    sort_sections(enrollments_feed)
    # Cache course and enrollment info
    NormalizedCacheEnrollment.update_enrollments(term_id=term_id, sid=cs_id, enrollments=enrollments)
    term_feed = {
        'termId': term_id,
        'termName': term_name,
        'enrollments': enrollments_feed,
        'enrolledUnits': enrolled_units,
        'unmatchedCanvasSites': [],
    }
    merge_drops_and_midterms(cs_id, term_name, term_feed)

    return term_feed


def check_for_multiple_primary_sections(enrollment, class_name, enrollments_by_class, section_feed):
    # If we have seen this class name before, in most cases we'll just append the new section feed to the
    # existing class feed. However, because multiple concurrent primary-section enrollments aren't distinguished by
    # class name, we need to do an extra check for that case.
    # TODO In the rare case of multiple-primary enrollments with associated secondary sections, secondary section
    # handling will be unpredictable.
    existing_primary = next((sec for sec in enrollments_by_class[class_name]['sections'] if is_enrolled_primary_section(sec)), None)
    # If we do indeed have two primary sections under the same class name, disambiguate them.
    if existing_primary:
        # First, revise the existing class feed to include section number.
        component = existing_primary['component']
        section = existing_primary['sectionNumber']
        disambiguated_class_name = f'{class_name} {component} {section}'
        enrollments_by_class[class_name]['displayName'] = disambiguated_class_name
        enrollments_by_class[disambiguated_class_name] = enrollments_by_class[class_name]
        del enrollments_by_class[class_name]
        # Now create a new class feed, also with section number, for our new primary section.
        component = section_feed['component']
        section = section_feed['sectionNumber']
        class_name = f'{class_name} {component} {section}'
        enrollments_by_class[class_name] = api_util.sis_enrollment_class_feed(enrollment)
        enrollments_by_class[class_name]['displayName'] = class_name
    return class_name


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


def is_enrolled_primary_section(section_feed):
    return section_feed['primary'] and section_feed['enrollmentStatus'] == 'E'


def merge_canvas_course_site(term_feed, site):
    if site['courseTerm'] != term_feed['termName']:
        return
    site_matched = False
    canvas_sections = data_loch.get_sis_sections_in_canvas_course(site['canvasCourseId'], term_feed['termId'])
    if not canvas_sections:
        return
    for canvas_section in canvas_sections:
        canvas_ccn = canvas_section['sis_section_id']
        if not canvas_ccn:
            continue
        for enrollment in term_feed['enrollments']:
            for sis_section in enrollment['sections']:
                if canvas_ccn == sis_section.get('ccn'):
                    sis_section['canvasCourseIds'] = sis_section.get('canvasCourseIds', [])
                    sis_section['canvasCourseIds'].append(site['canvasCourseId'])
                    if not site_matched:
                        enrollment['canvasSites'].append(site)
                    site_matched = True
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
        for section in enrollment['sections']:
            section['canvasCourseIds'] = sorted(section.get('canvasCourseIds', []))
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
