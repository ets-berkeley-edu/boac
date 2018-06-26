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

from boac.api.util import canvas_courses_api_feed
from boac.externals import data_loch
from boac.lib.analytics import mean_course_analytics_for_user
from boac.lib.berkeley import current_term_id, reverse_terms_until, sis_term_id_for_name, term_name_for_sis_id
from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.merged.sis_profile import get_merged_sis_profile
from boac.models.student import Student

"""Provide controller access to merged external data."""


def get_profiles(sid=None):
    # Currently, CalNet names and IDs are maintained in the Students table via a call to
    # "calnet.client(app).search_csids(sids)". Since the Students table mixes campus-wide
    # and ASC-specific data, this will probably change soon.
    student_storage = Student.find_by_sid(sid)
    if not student_storage:
        return None
    student_storage = student_storage.to_expanded_api_json()
    uid = student_storage['uid']
    athletics_profile = {
        'inIntensiveCohort': student_storage['inIntensiveCohort'],
        'isActiveAsc': student_storage['isActiveAsc'],
        'statusAsc': student_storage['statusAsc'],
        # This represents a join to another ASC-derived table, which might not have had a match.
        'athletics': student_storage.get('athletics', []),
    }
    canvas_profile = data_loch.get_user_for_uid(uid) or {}
    sis_profile = get_merged_sis_profile(sid)
    profiles = {
        'sid': student_storage['sid'],
        'uid': uid,
        'firstName': student_storage['firstName'],
        'lastName': student_storage['lastName'],
        'name': student_storage['name'],
        'canvasUserId': canvas_profile.get('canvas_id'),
        'canvasUserName': canvas_profile.get('name'),
        'sisProfile': sis_profile,
        'athleticsProfile': athletics_profile,
    }
    return profiles


def merge_student_terms(student, term_ids=None):
    if not student.get('sisProfile'):
        student['enrollmentTerms'] = []
        return student
    enrollment_terms = get_student_terms(
        student['uid'],
        student['sid'],
        student['canvasUserId'],
        student['sisProfile'].get('matriculation'),
        term_ids,
    )
    student['hasCurrentTermEnrollments'] = False
    for enrollment_term in enrollment_terms:
        if enrollment_term['termId'] == current_term_id():
            student['hasCurrentTermEnrollments'] = len(enrollment_term['enrollments']) > 0
            break
    student['enrollmentTerms'] = enrollment_terms
    return student


def get_student_terms(uid, sid, canvas_user_id, matriculation_term=None, term_ids=None):
    if term_ids == 'all':
        term_names = reverse_terms_until(matriculation_term)
        term_ids = [sis_term_id_for_name(t) for t in term_names]
    elif term_ids is None:
        term_ids = [current_term_id()]
    canvas_course_sites = data_loch.get_student_canvas_courses(uid) or []
    canvas_course_sites = canvas_courses_api_feed(canvas_course_sites)
    courses_by_term = []
    for term_id in term_ids:
        term_feed = merge_sis_enrollments_for_term(canvas_course_sites, uid, sid, term_name_for_sis_id(term_id))
        if term_feed and (len(term_feed['enrollments']) or len(term_feed['unmatchedCanvasSites'])):
            # Rebuild our Canvas courses list to remove any courses that were screened out during association (for instance,
            # dropped or athletic enrollments).
            canvas_courses = []
            for enrollment in term_feed.get('enrollments', []):
                canvas_courses += enrollment['canvasSites']
            canvas_courses += term_feed.get('unmatchedCanvasSites', [])
            # Decorate the Canvas courses list with per-course statistics, and return summary statistics.
            term_feed['analytics'] = mean_course_analytics_for_user(canvas_courses, canvas_user_id, term_id)
            courses_by_term.append(term_feed)
    return courses_by_term


def get_student_and_terms(sid, term_ids='all'):
    """Provide external data for student-specific view."""
    student_profile = get_profiles(sid)
    merge_student_terms(student_profile, term_ids)
    return student_profile


def merge_external_students_data(students, term_id=None):
    """Provide external data for multiple students in a given term.

    The students parameter must be a list of dicts which include an 'sid'.
    """
    term_ids = term_id and [term_id]
    for student in students:
        sid = student['sid']
        student_profile = get_profiles(sid)
        merge_student_terms(student_profile, term_ids)
        # Strip SIS details to lighten the API load.
        sis_profile = student_profile.pop('sisProfile', None)
        if sis_profile:
            student_profile['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
            student_profile['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
            student_profile['level'] = sis_profile.get('level', {}).get('description')
            student_profile['majors'] = sorted(plan.get('description') for plan in sis_profile.get('plans', []))
        # Lift the singleton term up.
        if len(student_profile['enrollmentTerms']):
            term = student_profile['enrollmentTerms'][0]
            del student_profile['enrollmentTerms']
            student_profile['analytics'] = term.pop('analytics')
            student_profile['term'] = term
        student.update(student_profile)
    return students
