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
from boac.externals import canvas
from boac.lib.analytics import mean_course_analytics_for_user
from boac.lib.berkeley import sis_term_id_for_name, term_name_for_sis_id
from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.merged.sis_profile import merge_sis_profile
from flask import current_app as app

"""Helper utils for cohort controller."""


def merge_all(member_feeds, term_id=None):
    if not term_id:
        term_name = app.config.get('CANVAS_CURRENT_ENROLLMENT_TERM')
        term_id = sis_term_id_for_name(term_name)
    for member_feed in member_feeds:
        _merge(member_feed, term_id)
    return member_feeds


def _merge(member_feed, term_id):
    uid = member_feed['uid']
    csid = member_feed['sid']
    cache_key = f'merged_data/{term_id}/{uid}'
    data = app.cache.get(cache_key) if app.cache else None
    if not data:
        data = _merged_data(uid, csid, term_id)
        if app.cache and data:
            app.cache.set(cache_key, data)
    if data:
        member_feed.update(data)
    return member_feed


def _merged_data(uid, csid, term_id):
    data = {}
    sis_profile = merge_sis_profile(csid)
    if sis_profile:
        data['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
        data['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
        data['level'] = sis_profile.get('level', {}).get('description')
        data['majors'] = sorted(plan.get('description') for plan in sis_profile.get('plans', []))
    canvas_profile = canvas.get_user_for_uid(uid)
    if canvas_profile:
        data['canvasUserId'] = canvas_profile['id']
        term_name = term_name_for_sis_id(term_id)
        student_courses = canvas.get_student_courses(uid) or []
        student_courses_in_term = [course for course in student_courses if course.get('term', {}).get('name') == term_name]
        canvas_courses = canvas_courses_api_feed(student_courses_in_term)
        # Associate course sites with campus enrollments.
        data['term'] = merge_sis_enrollments_for_term(canvas_courses, csid, term_name)
        # Rebuild our Canvas courses list to remove any courses that were screened out during association (for instance,
        # dropped or athletic enrollments).
        canvas_courses = []
        if data['term']:
            for enrollment in data['term'].get('enrollments', []):
                canvas_courses += enrollment['canvasSites']
            canvas_courses += data['term'].get('unmatchedCanvasSites', [])
        # Decorate the Canvas courses list with per-course statistics, and return summary statistics.
        data['analytics'] = mean_course_analytics_for_user(canvas_courses, uid, csid, canvas_profile['id'], term_id)
    return data
