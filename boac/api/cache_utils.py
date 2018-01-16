from threading import Thread
from boac import db, std_commit
from boac.lib import berkeley
from boac.merged.sis_profile import merge_sis_profile
from boac.models.job_progress import JobProgress
from boac.models.json_cache import JsonCache
from flask import current_app as app
from sqlalchemy import or_


def current_term_id():
    term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
    return berkeley.sis_term_id_for_name(term_name)


def refresh_request_handler(term_id, load_only=False):
    """Handle a start refresh admin request by returning an error status or starting the job on a background thread."""
    job_state = JobProgress().get()
    if job_state is None or (not job_state['start']) or job_state['end']:
        if not load_only:
            # Delete the current cache _before_ adding the JsonCache row that tracks job progress.
            clear_term(term_id)
        job_state = JobProgress().start()
        app.logger.warn('About to start background thread')
        app_arg = app._get_current_object()
        thread = Thread(target=background_thread_refresh, args=[app_arg, term_id], daemon=True)
        thread.start()
        return {
            'progress': job_state,
        }
    else:
        return {
            'error': 'Cannot start a new refresh job',
            'progress': job_state,
        }


def background_thread_refresh(app_arg, term_id):
    with app_arg.app_context():
        load_term(term_id)


def refresh_term(term_id=current_term_id()):
    clear_term(term_id)
    load_term(term_id)


def clear_term(term_id):
    """Delete term-specific cache entries.

    When refreshing current term, also deletes non-term-specific cache entries, since they hold 'current' external data.
    """
    term_name = berkeley.term_name_for_sis_id(term_id)
    filter = JsonCache.key.like('term_{}%'.format(term_name))
    if term_name == app.config['CANVAS_CURRENT_ENROLLMENT_TERM']:
        filter = or_(filter, JsonCache.key.notlike('term_%'))
    matches = db.session.query(JsonCache).filter(filter)
    app.logger.info('Will delete {} entries'.format(matches.count()))
    matches.delete(synchronize_session=False)
    std_commit()


def load_term(term_id=current_term_id()):
    from boac.models.student import Student
    success_count = 0
    failures = []

    for csid, uid in db.session.query(Student.sid, Student.uid).distinct():
        s, f = load_canvas_externals(uid, term_id)
        success_count += s
        failures += f
        s, f = load_sis_externals(term_id, csid)
        success_count += s
        failures += f
        JobProgress().update(f'External data loaded for UID {uid}')

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


def load_merged_sis_profiles():
    """TODO For now, pending one merged model refresh strategy, this sits to the side of other cache loading methods."""
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
