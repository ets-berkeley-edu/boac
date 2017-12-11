"""Helper utils for cohort controller"""

from boac.api.util import canvas_courses_api_feed
from boac.externals import canvas
from boac.lib.analytics import mean_course_analytics_for_user
from boac.lib.berkeley import sis_term_id_for_name
from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.merged.sis_profile import merge_sis_profile
from flask import current_app as app


def merge_all(member_feeds):
    for member_feed in member_feeds:
        merge(member_feed)
    return member_feeds


def merge(member_feed):
    uid = member_feed['uid']
    csid = member_feed['sid']
    data_cache_key = 'merged_data/{}'.format(uid)
    data = app.cache.get(data_cache_key) if app.cache else None
    if not data:
        data = merged_data(uid, csid)
        if app.cache and data:
            app.cache.set(data_cache_key, data)
    if data:
        member_feed.update(data)
    return member_feed


def merged_data(uid, csid):
    data = {}
    sis_profile = merge_sis_profile(csid)
    if sis_profile:
        data['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
        data['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
        data['level'] = sis_profile.get('level', {}).get('description')
        data['majors'] = [plan.get('description') for plan in sis_profile.get('plans', [])]
    canvas_profile = canvas.get_user_for_uid(uid)
    if canvas_profile:
        data['avatar_url'] = canvas_profile['avatar_url']
        student_courses = canvas.get_student_courses(uid) or []
        current_term = app.config.get('CANVAS_CURRENT_ENROLLMENT_TERM')
        term_id = sis_term_id_for_name(current_term)
        student_courses_in_current_term = [course for course in student_courses if
                                           course.get('term', {}).get('name') == current_term]
        canvas_courses = canvas_courses_api_feed(student_courses_in_current_term)
        # Decorate the Canvas courses list with per-course statistics, and return summary statistics.
        data['analytics'] = mean_course_analytics_for_user(canvas_courses, canvas_profile['id'], term_id)
        # Associate those course sites with campus enrollments.
        data['currentTerm'] = merge_sis_enrollments_for_term(canvas_courses, csid, current_term)
    return data
