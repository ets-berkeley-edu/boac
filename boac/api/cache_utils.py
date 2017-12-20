from threading import Thread
from boac import db
from boac.lib import berkeley
from boac.models.job_progress import JobProgress
from boac.models.json_cache import JsonCache
from flask import current_app as app


def refresh_request_handler(load_only=False):
    """Handle a start refresh admin request, either by returning an error status or by starting the job on a
    background thread.
    """
    job_state = JobProgress().get()
    if job_state is None or (not job_state['start']) or job_state['end']:
        job_state = JobProgress().start()
        app.logger.warn('About to start background thread')
        app_arg = app._get_current_object()
        thread = Thread(target=background_thread_refresh, args=[app_arg, load_only], daemon=True)
        thread.start()
        return {
            'progress': job_state,
        }
    else:
        return {
            'error': 'Cannot start a new refresh job',
            'progress': job_state,
        }


def background_thread_refresh(app_arg, load_only):
    with app_arg.app_context():
        _background_thread_refresh(load_only)


def _background_thread_refresh(load_only):
    """TODO Work-in-progress mock refresh which does not actually remove any existing cache.
    When we feel more confident about our background-job-running approach, we'll add the riskier, more
    time-consuming logic, and refactor existing scripts.

    if not load_only: ....
    """
    from boac.models.student import Student
    success_count = 0
    failures = []
    term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
    sis_term_id = berkeley.sis_term_id_for_name(term_name)

    for csid, uid in db.session.query(Student.sid, Student.uid).distinct():
        s, f = load_canvas_externals(uid, sis_term_id)
        success_count += s
        failures += f
        s, f = load_sis_externals(sis_term_id, csid)
        success_count += s
        failures += f
        s, f = load_canvas_scores(uid, sis_term_id)
        success_count += s
        failures += f
        JobProgress().update(f'External data loaded for UID {uid}')

    JobProgress().end()
    app.logger.warn('Complete. Fetched {} external feeds.'.format(success_count))
    if len(failures):
        app.logger.warn('Failed to fetch {} feeds:'.format(len(failures)))
        app.logger.warn(failures)


def clear_current_term(include_canvas_scores=False):
    # When refreshing the current term, also delete non-term-specific cache entries which hold 'current' external
    # data.
    filters = [
        JsonCache.key.notlike('term_%'),
        JsonCache.key.like('term_{}%'.format(app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])),
    ]
    # The Canvas course scores feeds are currently too time-consuming to toss aside lightly.
    exclude_canvas_scores_filters = [
        JsonCache.key.notlike('%canvas_course_enrollments%'),
        JsonCache.key.notlike('%canvas_course_assignments_analytics%'),
    ]
    if not include_canvas_scores:
        filters += exclude_canvas_scores_filters
    matches = db.session.query(JsonCache).filter(*filters)
    app.logger.info('Will delete {} entries'.format(matches.count()))
    matches.delete(synchronize_session=False)
    db.session.commit()


def load_canvas_externals(uid, sis_term_id):
    from boac.externals import canvas

    success_count = 0
    failures = []

    canvas_user_profile = canvas.get_user_for_uid(uid)
    if canvas_user_profile is None:
        failures.append('canvas.get_user_for_uid failed for UID {}'.format(
            uid,
        ))
    elif canvas_user_profile:
        success_count += 1
        sites = canvas.get_student_courses(uid)
        if sites:
            success_count += 1
            for site in sites:
                if site.get('term', {}).get('name') != berkeley.term_name_for_sis_id(sis_term_id):
                    continue
                site_id = site['id']
                if not canvas.get_course_sections(site_id, sis_term_id):
                    failures.append('canvas.get_course_sections failed for UID {}, site_id {}'.format(
                        uid,
                        site_id,
                    ))
                    continue
                success_count += 1
                if not canvas.get_student_summaries(site_id, sis_term_id):
                    failures.append('canvas.get_student_summaries failed for site_id {}'.format(
                        site_id,
                    ))
                    continue
                success_count += 1
    return success_count, failures


def load_canvas_scores(uid, sis_term_id):
    from boac.externals import canvas

    success_count = 0
    failures = []

    canvas_user_profile = canvas.get_user_for_uid(uid)
    if canvas_user_profile is None:
        failures.append('canvas.get_user_for_uid failed for UID {}'.format(
            uid,
        ))
    elif canvas_user_profile:
        success_count += 1
        sites = canvas.get_student_courses(uid)
        if sites:
            success_count += 1
            for site in sites:
                site_id = site['id']
                if not canvas.get_course_enrollments(site_id, sis_term_id):
                    failures.append('canvas.get_course_enrollments failed for site_id {}'.format(
                        site_id,
                    ))
                    continue
                success_count += 1

    return success_count, failures


def load_all_canvas_scores(sis_term_id=None):
    from boac.lib import berkeley
    from boac.models.student import Student

    success_count = 0
    failures = []

    if sis_term_id is None:
        term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
        sis_term_id = berkeley.sis_term_id_for_name(term_name)

    for row in db.session.query(Student.uid).distinct():
        uid = row[0]
        s, f = load_canvas_scores(uid, sis_term_id)
        success_count += s
        failures += f

    app.logger.warn('Complete. Fetched {} external feeds.'.format(success_count))
    if len(failures):
        app.logger.warn('Failed to fetch {} feeds:'.format(len(failures)))
        app.logger.warn(failures)


def load_sis_externals(sis_term_id, csid):
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
                    failures.append('SIS get_degree_progresss failed for CSID {}'.format(csid))
    else:
        failures.append('SIS get_student failed for CSID {}'.format(csid))

    enrollments = sis_enrollments_api.get_enrollments(csid, sis_term_id)
    if enrollments:
        success_count += 1
    elif enrollments is None:
        failures.append('SIS get_enrollments failed for CSID {}, sis_term_id {}'.format(
            csid,
            sis_term_id,
        ))
    return success_count, failures


def load_current_term():
    from boac.models.student import Student

    success_count = 0
    failures = []

    term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
    sis_term_id = berkeley.sis_term_id_for_name(term_name)

    # Currently, all external data is loaded starting from the individuals who belong
    # to one or more Cohorts.
    for csid, uid in db.session.query(Student.sid, Student.uid).distinct():
        s, f = load_canvas_externals(uid, sis_term_id)
        success_count += s
        failures += f
        s, f = load_sis_externals(sis_term_id, csid)
        success_count += s
        failures += f

    app.logger.warn('Complete. Fetched {} external feeds.'.format(success_count))
    if len(failures):
        app.logger.warn('Failed to fetch {} feeds:'.format(len(failures)))
        app.logger.warn(failures)


def refresh_current_term():
    clear_current_term()
    load_current_term()
