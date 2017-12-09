"""Helper utils for cohort controller"""

from boac.api.util import canvas_courses_api_feed
from boac.externals import canvas
from boac.lib.analytics import mean_course_analytics_for_user
from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.merged.sis_profile import merge_sis_profile
from flask import current_app as app


def merge(member_feed):
    sis_profile = merge_sis_profile(member_feed['sid'])
    if sis_profile:
        member_feed['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
        member_feed['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
        member_feed['level'] = sis_profile.get('level', {}).get('description')
        member_feed['majors'] = [plan.get('description') for plan in sis_profile.get('plans', [])]

    uid = member_feed['uid']
    cache_key = 'user/{uid}'.format(uid=uid)
    canvas_profile = app.cache.get(cache_key) if app.cache else None
    if not canvas_profile:
        canvas_profile = canvas.get_user_for_uid(uid)
        # Cache Canvas profiles
        if app.cache and canvas_profile:
            app.cache.set(cache_key, canvas_profile)

    if canvas_profile:
        member_feed['avatar_url'] = canvas_profile['avatar_url']
        student_courses = canvas.get_student_courses(uid) or []
        current_term = app.config.get('CANVAS_CURRENT_ENROLLMENT_TERM')
        student_courses_in_current_term = [course for course in student_courses if
                                           course.get('term', {}).get('name') == current_term]
        canvas_courses = canvas_courses_api_feed(student_courses_in_current_term)
        member_feed['analytics'] = mean_course_analytics_for_user(canvas_courses,
                                                                  canvas_profile['id'],
                                                                  current_term)
        # The call to mean_course_analytics_for_user, above, has enriched the canvas_courses
        # list with per-course statistics. Next, associate those course sites with enrollments.
        member_feed['currentTerm'] = merge_sis_enrollments_for_term(canvas_courses,
                                                                    member_feed['sid'],
                                                                    current_term)
    return member_feed


def merge_all(member_feeds):
    for member_feed in member_feeds:
        merge(member_feed)
    return member_feeds
