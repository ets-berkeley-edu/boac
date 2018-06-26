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
from boac.externals import data_loch, sis_degree_progress_api, sis_enrollments_api, sis_student_api
from boac.lib import berkeley
from boac.merged import import_asc_athletes
from boac.merged.calnet import merge_student_calnet_data
from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.merged.sis_profile import get_merged_sis_profile
from boac.models import json_cache
from boac.models.alert import Alert
from boac.models.job_progress import JobProgress
from boac.models.json_cache import JsonCache
from boac.models.normalized_cache_enrollment import NormalizedCacheEnrollment
from boac.models.normalized_cache_student import NormalizedCacheStudent
from boac.models.normalized_cache_student_major import NormalizedCacheStudentMajor
from boac.models.student import Student
from flask import current_app as app
from sqlalchemy import and_, or_


def refresh_request_handler(term_id, load_only=False, import_asc=False):
    """Handle a start refresh admin request by returning an error status or starting the job on a background thread."""
    job_state = JobProgress().get()
    if job_state is None or (not job_state['start']) or job_state['end']:
        job_type = 'Load' if load_only else 'Refresh'
        JobProgress().start({
            'job_type': job_type,
            'term_id': term_id,
            'import_asc': import_asc,
        })
        app.logger.warn('About to start background thread')
        thread = Thread(
            target=background_thread_refresh,
            daemon=True,
            kwargs={
                'app_arg': app._get_current_object(),
                'term_id': term_id,
                'job_type': job_type,
                'import_asc': import_asc,
            },
        )
        thread.start()
        return {
            'progress': JobProgress().get(),
        }
    else:
        return {
            'error': 'Cannot start a new refresh job',
            'progress': job_state,
        }


def continue_request_handler():
    """Continue an interrupted cache refresh or load job (skipping the optional ASC import)."""
    # WARNING: There is currently no protection against duplicate continuation requests. Admins need to ensure
    # that the refresh job is currently inactive.

    job_state = JobProgress().get()
    if job_state and job_state['start'] and not job_state['end']:
        job_type = job_state['job_type']
        term_id = job_state['term_id']
        JobProgress().update(f'Continuing {job_type} for term {term_id}')
        thread = Thread(
            target=background_thread_refresh,
            daemon=True,
            kwargs={
                'app_arg': app._get_current_object(),
                'term_id': term_id,
                'job_type': job_type,
                'continuation': True,
            },
        )
        thread.start()
        return {
            'progress': JobProgress().get(),
        }
    else:
        return {
            'error': 'Cannot continue this refresh job',
            'progress': job_state,
        }


def background_thread_refresh(app_arg, term_id, job_type, import_asc=False, continuation=False):
    with app_arg.app_context():
        try:
            if import_asc:
                do_import_asc()
            if job_type == 'Refresh':
                refresh_term(term_id, continuation)
            else:
                load_term(term_id)
            JobProgress().end()
        except Exception as e:
            app.logger.exception(e)
            app.logger.error('Background thread is stopping')
            JobProgress().update(f'An unexpected error occured: {e}')
            raise e


def refresh_term(term_id=berkeley.current_term_id(), continuation=False):
    if not continuation or not json_cache.staging_table_exists():
        JobProgress().update(f'About to drop/create staging table')
        json_cache.drop_staging_table()
        json_cache.create_staging_table(exclusions_for_term(term_id))
    json_cache.set_staging(True)
    load_term(term_id)
    JobProgress().update(f'About to refresh from staging table')
    refresh_count = json_cache.refresh_from_staging(inclusions_for_term(term_id))
    if refresh_count == 0:
        JobProgress().update('ERROR: No cache entries copied from staging')
    else:
        JobProgress().update(f'{refresh_count} cache entries copied from staging')


def exclusions_for_term(term_id):
    if term_id == 'all':
        # Start with an empty staging table.
        return 'key IS NULL'

    term_name = berkeley.term_name_for_sis_id(term_id)
    where_clause = f'key NOT LIKE \'term_{term_name}%\''
    # If we are refreshing current data, we only keep stowed entries which are explicitly keyed to past terms.
    if term_name == app.config['CANVAS_CURRENT_ENROLLMENT_TERM']:
        where_clause += ' AND key LIKE \'term_%\''
    return where_clause


def inclusions_for_term(term_id):
    if term_id == 'all':
        return 'key NOT LIKE \'asc_athletes_%\' AND key NOT LIKE \'job%\''

    term_name = berkeley.term_name_for_sis_id(term_id)
    where_clause = f'key LIKE \'term_{term_name}%\''
    if term_name == app.config['CANVAS_CURRENT_ENROLLMENT_TERM']:
        where_clause += ' OR (key NOT LIKE \'term_%\' AND key NOT LIKE \'asc_athletes_%\' AND key NOT LIKE \'job%\')'
    return where_clause


def clear_term(term_id):
    """Delete term-specific cache entries.

    When refreshing current term, also deletes most non-term-specific cache entries, since they hold 'current' external data.
    Application-supporting history must be explicitly excluded.
    """
    term_name = berkeley.term_name_for_sis_id(term_id)
    _filter = JsonCache.key.like(f'term_{term_name}%')
    if term_name == app.config['CANVAS_CURRENT_ENROLLMENT_TERM']:
        current_externals_filter = and_(
            JsonCache.key.notlike('term_%'),
            JsonCache.key.notlike('asc_athletes_%'),
            JsonCache.key.notlike('job_%'),
        )
        _filter = or_(_filter, current_externals_filter)
    matches = db.session.query(JsonCache).filter(_filter)
    app.logger.info(f'Will delete {matches.count()} entries')
    matches.delete(synchronize_session=False)
    std_commit()


def cancel_refresh_in_progress(term_id):
    progress = JobProgress().get()
    if progress and progress['job_type'] == 'Refresh':
        # Drop the staging table.
        json_cache.drop_staging_table()
    progress = JobProgress().delete()
    return {
        'progressDeleted': progress,
    }


def do_import_asc():
    status = import_asc_athletes.update_from_asc_api()
    JobProgress().update(f'ASC import finished: {status}')


def get_all_student_ids():
    # Return all query results as a static list object. If we instead iterated over the Query object to
    # fetch one row at a time, multiple iterations would re-run the query from scratch. This can
    # lead to inconsistencies between different parts of the new cache.
    return db.session.query(Student.sid, Student.uid).distinct().all()


def load_all_terms():
    job_progress = JobProgress().get()
    terms_done = job_progress.get('terms_done', [])
    all_terms = berkeley.all_term_ids()
    while terms_done != all_terms:
        if len(terms_done) == len(all_terms):
            app.logger.error(f'Unexpected terms_done value; stopping load: {terms_done}')
            return
        term_id = next(t for t in all_terms if t not in terms_done)
        load_term(term_id)
        terms_done.append(term_id)
        JobProgress().update(f'Term {term_id} loaded', properties={'terms_done': terms_done})


def load_term(term_id=berkeley.current_term_id()):
    if term_id == 'all':
        load_all_terms()
        return

    success_count = 0
    failures = []

    # Load CalNet attributes from LDAP, including any missing UIDs.
    merge_student_calnet_data()

    ids = get_all_student_ids()
    nbr_students = len(ids)
    nbr_finished = 0
    for csid, uid in ids:
        s, f = load_canvas_externals(uid, term_id)
        success_count += s
        failures += f
        s, f = load_sis_externals(uid, csid, term_id)
        success_count += s
        failures += f
        nbr_finished += 1
        if (nbr_finished == nbr_students) or not (nbr_finished % math.ceil(nbr_students / 20)):
            JobProgress().update(f'External data loaded for {nbr_finished} of {nbr_students} students')

    JobProgress().update(f'About to load analytics feeds')
    nbr_finished = 0
    for csid, uid in ids:
        load_analytics_feeds(uid, csid, term_id)
        nbr_finished += 1
        if (nbr_finished == nbr_students) or not (nbr_finished % math.ceil(nbr_students / 20)):
            JobProgress().update(f'Analytics feeds loaded for {nbr_finished} of {nbr_students} students')

    if term_id == berkeley.current_term_id():
        JobProgress().update(f'About to load merged profiles for current term')
        load_merged_sis_profiles(ids)

    JobProgress().update(f'About to load normalized cache for current term')
    load_normalized_cache(term_id, ids)

    JobProgress().update(f'About to load alerts for current term')
    load_alerts(term_id, ids)

    app.logger.warn(f'Term {term_id} load complete. Fetched {success_count} external feeds.')
    if len(failures):
        app.logger.warn(f'Failed to fetch {len(failures)} feeds:')
        app.logger.warn(failures)


def load_canvas_externals(uid, term_id):
    success_count = 0
    failures = []

    canvas_user_profile = data_loch.get_user_for_uid(uid)
    if not canvas_user_profile:
        failures.append(f'data_loch.get_user_for_uid failed for UID {uid}')
    elif canvas_user_profile:
        success_count += 1
        sites = data_loch.get_student_canvas_courses(uid)
        if sites is None:
            failures.append(f'data_loch.get_student_canvas_courses failed for UID {uid}')
        else:
            success_count += 1
            term_name = berkeley.term_name_for_sis_id(term_id)
            for site in sites:
                if site.get('canvas_course_term') != term_name:
                    continue
                site_id = site['canvas_course_id']
                if not data_loch.get_sis_sections_in_canvas_course(site_id, term_id):
                    failures.append(f'data_loch.get_sis_sections_in_canvas_course failed for UID {uid}, site_id {site_id}')
                    continue
                success_count += 1
    return success_count, failures


def load_sis_externals(uid, csid, term_id):
    term_name = berkeley.term_name_for_sis_id(term_id)

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

    enrollments = data_loch.get_sis_enrollments(uid, term_id) or []
    if term_name == app.config['CANVAS_CURRENT_ENROLLMENT_TERM']:
        sis_enrollments_api.get_drops_and_midterms(csid, term_id)

    if enrollments:
        success_count += 1
    elif enrollments is None:
        failures.append(f'get_sis_enrollments failed for CSID {csid}, term_id {term_id}')
    return success_count, failures


def load_analytics_feeds(uid, sid, term_id):
    # Load distilled analytics feeds, one level up from the Canvas APIs already called by load_canvas_externals.
    canvas_user_profile = data_loch.get_user_for_uid(uid)
    canvas_user_id = canvas_user_profile and canvas_user_profile['canvas_id']
    student_courses = data_loch.get_student_canvas_courses(uid)
    canvas_courses_feed = canvas_courses_api_feed(student_courses)
    # Route the course site feed through our SIS enrollments merge, so that site selection logic (e.g., filtering
    # out dropped and athletic enrollments) is consistent with web API calls.
    term_name = berkeley.term_name_for_sis_id(term_id)
    merged_term_feed = merge_sis_enrollments_for_term(canvas_courses_feed, uid, sid, term_name)

    def load_analytics_for_sites(sites):
        for site in sites:
            data_loch.get_canvas_course_scores(site['canvasCourseId'], term_id)
            if canvas_user_id:
                data_loch.get_submissions_turned_in_relative_to_user(site['canvasCourseId'], canvas_user_id, term_id)
    if merged_term_feed:
        for enrollment in merged_term_feed['enrollments']:
            load_analytics_for_sites(enrollment['canvasSites'])
        load_analytics_for_sites(merged_term_feed['unmatchedCanvasSites'])


def load_merged_sis_profiles(ids=None):
    if not ids:
        ids = get_all_student_ids()
    success_count = 0
    failures = []

    for csid, uid in ids:
        sis_profile = get_merged_sis_profile(csid)
        if sis_profile:
            success_count += 1
        else:
            failures.append(f'get_merged_sis_profile failed for SID {csid}')
    return success_count, failures


def load_normalized_cache(term_id, ids=None):
    if not ids:
        ids = get_all_student_ids()
    for csid, uid in ids:
        # Load normalized enrollments table supporting BOAC's course-specific pages.
        NormalizedCacheEnrollment.update_enrollments(term_id, uid, csid)
        # If loading the current term, also update the normalized profiles table to support team and cohort searches.
        if term_id == berkeley.current_term_id():
            sis_profile = get_merged_sis_profile(csid)
            if not sis_profile:
                continue
            gpa = sis_profile.get('cumulativeGPA')
            level = sis_profile.get('level', {}).get('description')
            units = sis_profile.get('cumulativeUnits')
            NormalizedCacheStudent.update_profile(csid, gpa=gpa, level=level, units=units)

            majors = [plan['description'] for plan in sis_profile.get('plans', [])]
            NormalizedCacheStudentMajor.update_majors(csid, majors)


def load_alerts(term_id, ids=None):
    if not ids:
        ids = get_all_student_ids()
    # TODO Reinstate assignment alerts based on loch data.
    for csid, uid in ids:
        term_feed = json_cache.fetch(f'merged_enrollment_{csid}', term_id=term_id)
        if not term_feed:
            continue
        for enrollment in term_feed['enrollments']:
            for section in enrollment['sections']:
                if section.get('midtermGrade'):
                    Alert.update_midterm_grade_alerts(csid, term_id, section['ccn'], enrollment['displayName'], section['midtermGrade'])
