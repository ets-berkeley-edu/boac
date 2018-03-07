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


import math
from threading import Thread
from boac import db, std_commit
from boac.api.util import canvas_courses_api_feed
from boac.lib import analytics
from boac.lib import berkeley
from boac.merged import import_asc_athletes
from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.merged.sis_profile import merge_sis_profile
from boac.models.alert import Alert
from boac.models.job_progress import JobProgress
from boac.models.json_cache import JsonCache
from flask import current_app as app
from sqlalchemy import and_, or_


def refresh_request_handler(term_id, load_only=False, import_asc=False):
    """Handle a start refresh admin request by returning an error status or starting the job on a background thread."""
    job_state = JobProgress().get()
    if job_state is None or (not job_state['start']) or job_state['end']:
        if not load_only:
            # Delete the current cache _before_ adding the JsonCache row that tracks job progress.
            clear_term(term_id)
        JobProgress().start()
        job_type = 'Load' if load_only else 'Refresh'
        JobProgress().update(f'{job_type} term {term_id}; import ASC data = {import_asc}')
        app.logger.warn('About to start background thread')
        app_arg = app._get_current_object()
        thread = Thread(target=background_thread_refresh, args=[app_arg, term_id, import_asc], daemon=True)
        thread.start()
        return {
            'progress': JobProgress().get(),
        }
    else:
        return {
            'error': 'Cannot start a new refresh job',
            'progress': job_state,
        }


def background_thread_refresh(app_arg, term_id, import_asc):
    with app_arg.app_context():
        try:
            if import_asc:
                do_import_asc()
            load_term(term_id)
        except Exception as e:
            app.logger.exception(e)
            app.logger.error('Background thread is stopping')
            JobProgress().update(f'An unexpected error occured: {e}')
            raise e


def refresh_term(term_id=berkeley.current_term_id()):
    clear_term(term_id)
    load_term(term_id)


def clear_term(term_id):
    """Delete term-specific cache entries.

    When refreshing current term, also deletes most non-term-specific cache entries, since they hold 'current' external data.
    Application-supporting history must be explicitly excluded.
    """
    term_name = berkeley.term_name_for_sis_id(term_id)
    filter = JsonCache.key.like('term_{}%'.format(term_name))
    if term_name == app.config['CANVAS_CURRENT_ENROLLMENT_TERM']:
        current_externals_filter = and_(
            JsonCache.key.notlike('term_%'),
            JsonCache.key.notlike('asc_athletes_%'),
            JsonCache.key.notlike('job_%'),
        )
        filter = or_(filter, current_externals_filter)
    matches = db.session.query(JsonCache).filter(filter)
    app.logger.info('Will delete {} entries'.format(matches.count()))
    matches.delete(synchronize_session=False)
    std_commit()


def do_import_asc():
    status = import_asc_athletes.update_from_asc_api()
    JobProgress().update(f'ASC import finished: {status}')


def load_term(term_id=berkeley.current_term_id()):
    from boac.models.student import Student
    success_count = 0
    failures = []

    ids = db.session.query(Student.sid, Student.uid).distinct()
    nbr_students = ids.count()
    nbr_finished = 0
    for csid, uid in ids:
        s, f = load_canvas_externals(uid, term_id)
        success_count += s
        failures += f
        s, f = load_sis_externals(term_id, csid)
        success_count += s
        failures += f
        nbr_finished += 1
        if (nbr_finished == nbr_students) or not (nbr_finished % math.ceil(nbr_students / 20)):
            JobProgress().update(f'External data loaded for {nbr_finished} of {nbr_students} athletes')

    for csid, uid in ids:
        load_analytics_feeds(uid, csid, term_id)

    # Given a fresh start with no existing 'normalized' cache, merged profiles must be pre-fetched.
    # Otherwise all team and cohort searches will return empty arrays in the UX.
    if term_id == berkeley.current_term_id():
        load_merged_sis_profiles()

    JobProgress().end()
    app.logger.warn('Complete. Fetched {} external feeds.'.format(success_count))
    if len(failures):
        app.logger.warn('Failed to fetch {} feeds:'.format(len(failures)))
        app.logger.warn(failures)


def load_canvas_externals(uid, term_id):
    from boac.externals import canvas

    success_count = 0
    failures = []

    canvas_user_profile = canvas.get_user_for_uid(uid)
    if canvas_user_profile is None:
        failures.append(f'canvas.get_user_for_uid failed for UID {uid}')
    elif canvas_user_profile:
        success_count += 1
        sites = canvas.get_student_courses(uid)
        if sites is None:
            failures.append(f'canvas.get_student_courses failed for UID {uid}')
        else:
            success_count += 1
            term_name = berkeley.term_name_for_sis_id(term_id)
            for site in sites:
                if site.get('term', {}).get('name') != term_name:
                    continue
                site_id = site['id']
                if not canvas.get_course_sections(site_id, term_id):
                    failures.append(f'canvas.get_course_sections failed for UID {uid}, site_id {site_id}')
                    continue
                success_count += 1
                if not canvas.get_student_summaries(site_id, term_id):
                    failures.append(f'canvas.get_student_summaries failed for site_id {site_id}')
                    continue
                success_count += 1
                # This is a very time-consuming API and might have to managed separately.
                if not canvas.get_course_enrollments(site_id, term_id):
                    failures.append(f'canvas.get_course_enrollments failed for site_id {site_id}')
                    continue
                success_count += 1
                # Do not treat an empty list as a failure.
                if canvas.get_assignments_analytics(site_id, uid, term_id) is None:
                    failures.append(f'canvas.get_assignments_analytics failed for UID {uid}, site_id {site_id}')
                    continue
                success_count += 1
    return success_count, failures


def load_sis_externals(term_id, csid):
    from boac.externals import sis_degree_progress_api, sis_enrollments_api, sis_student_api

    success_count = 0
    failures = []

    sis_response = sis_student_api.get_student(csid)
    if sis_response:
        success_count += 1
        academic_statuses = sis_response.get('academicStatuses')
        if academic_statuses and (len(academic_statuses) > 0):
            if academic_statuses[0].get('currentRegistration', {}).get('academicCareer', {}).get('code') == 'UGRD':
                if sis_degree_progress_api.get_degree_progress(csid):
                    success_count += 1
                else:
                    failures.append(f'SIS get_degree_progresss failed for CSID {csid}')
    else:
        failures.append(f'SIS get_student failed for CSID {csid}')

    enrollments = sis_enrollments_api.get_enrollments(csid, term_id)
    if enrollments:
        success_count += 1
    elif enrollments is None:
        failures.append(f'SIS get_enrollments failed for CSID {csid}, term_id {term_id}')
    return success_count, failures


def load_analytics_feeds(uid, sid, term_id):
    # Load distilled analytics feeds, one level up from the Canvas APIs already called by load_canvas_externals.
    # Prior to load, existing assignment alerts for the student and term are deactivated. Alerts still in effect
    # will be reactivated as feeds are loaded.
    Alert.deactivate_all(sid=sid, term_id=term_id, alert_types=['late_assignment', 'missing_assignment'])
    from boac.externals import canvas
    student_courses = canvas.get_student_courses(uid)
    canvas_courses_feed = canvas_courses_api_feed(student_courses)
    # Route the course site feed through our SIS enrollments merge, so that site selection logic (e.g., filtering
    # out dropped and athletic enrollments) is consistent with web API calls.
    term_name = berkeley.term_name_for_sis_id(term_id)
    merged_term_feed = merge_sis_enrollments_for_term(canvas_courses_feed, sid, term_name)

    def load_analytics_for_sites(sites):
        for site in sites:
            analytics.analytics_from_canvas_course_assignments(
                course_id=site['canvasCourseId'],
                course_code=site['courseCode'],
                uid=uid,
                sid=sid,
                term_id=term_id,
            )
    if merged_term_feed:
        for enrollment in merged_term_feed['enrollments']:
            load_analytics_for_sites(enrollment['canvasSites'])
        load_analytics_for_sites(merged_term_feed['unmatchedCanvasSites'])


def load_merged_sis_profiles():
    from boac.models.student import Student

    success_count = 0
    failures = []

    for (sid,) in db.session.query(Student.sid).distinct():
        sis_profile = merge_sis_profile(sid)
        if sis_profile:
            success_count += 1
        else:
            failures.append(f'merge_sis_profile failed for SID {sid}')
    return success_count, failures
