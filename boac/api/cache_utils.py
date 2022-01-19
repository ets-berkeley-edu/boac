"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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


import re
from threading import Thread

from boac import std_commit
from boac.externals import data_loch
from boac.merged.sis_terms import all_term_ids, current_term_id
from boac.models.alert import Alert
from boac.models.curated_group import CuratedGroupStudent
from boac.models.job_progress import JobProgress
from flask import current_app as app


def refresh_request_handler(term_id):
    """Handle a start refresh admin request by returning an error status or starting the job on a background thread."""
    job_state = JobProgress().get()

    if job_state and job_state['start'] and not job_state['end']:
        app.logger.error(f'Previous refresh job did not finish normally: {job_state}')
        JobProgress().delete()

    JobProgress().start({
        'term_id': term_id,
    })
    app.logger.warn('About to start background thread')
    thread = Thread(
        target=background_thread_refresh,
        daemon=True,
        kwargs={
            'app_arg': app._get_current_object(),
            'term_id': term_id,
        },
    )
    thread.start()
    return {
        'progress': JobProgress().get(),
    }


def continue_request_handler():
    """Continue an interrupted cache refresh or load job (skipping the optional ASC import)."""
    # WARNING: There is currently no protection against duplicate continuation requests. Admins need to ensure
    # that the refresh job is currently inactive.

    job_state = JobProgress().get()
    if job_state and job_state['start'] and not job_state['end']:
        term_id = job_state['term_id']
        thread = Thread(
            target=background_thread_refresh,
            daemon=True,
            kwargs={
                'app_arg': app._get_current_object(),
                'term_id': term_id,
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


def background_thread_refresh(app_arg, term_id):
    with app_arg.app_context():
        try:
            refresh_current_term_index()
            load_term(term_id)
            JobProgress().end()
        except Exception as e:
            app.logger.exception(e)
            app.logger.error('Background thread is stopping')
            JobProgress().update(f'An unexpected error occured: {e}')
            raise e


def load_all_terms():
    job_progress = JobProgress().get()
    terms_done = job_progress.get('terms_done', [])
    all_terms = all_term_ids()
    while terms_done != all_terms:
        if len(terms_done) == len(all_terms):
            app.logger.error(f'Unexpected terms_done value; stopping load: {terms_done}')
            return
        term_id = next(t for t in all_terms if t not in terms_done)
        load_term(term_id)
        terms_done.append(term_id)
        JobProgress().update(f'Term {term_id} loaded', properties={'terms_done': terms_done})


def load_term(term_id=current_term_id(use_cache=False)):
    if term_id == 'all':
        load_all_terms()
        return

    JobProgress().update(f'About to refresh alerts for term {term_id}')
    refresh_alerts(term_id)

    if term_id == current_term_id():
        JobProgress().update('About to refresh department memberships')
        refresh_department_memberships()
        JobProgress().update('About to refresh CalNet attributes for active users')
        refresh_calnet_attributes()
        JobProgress().update('About to load filtered cohort counts')
        load_filtered_cohort_counts()
        JobProgress().update('About to update curated group memberships')
        update_curated_group_lists()


def refresh_alerts(term_id):
    Alert.deactivate_all_for_term(term_id)
    Alert.update_all_for_term(term_id)


def refresh_calnet_attributes():
    from boac.merged import calnet
    from boac.models.authorized_user import AuthorizedUser
    from boac.models import json_cache
    active_uids = {u.uid for u in AuthorizedUser.get_all_active_users()}
    json_cache.clear('calnet_user_for_uid_%')
    new_attrs = calnet.get_calnet_users_for_uids(app, active_uids)
    app.logger.info(f'Cached {len(new_attrs)} CalNet records for {len(active_uids)} active users')


def refresh_current_term_index():
    from boac.merged import sis_terms
    from boac.models import json_cache
    json_cache.clear('current_term_index')
    sis_terms.get_current_term_index()
    app.logger.info('Cached current and future SIS terms')


def refresh_department_memberships():
    from boac.models.authorized_user import AuthorizedUser
    from boac.models.authorized_user_extension import DropInAdvisor, SameDayAdvisor, Scheduler
    from boac.models.university_dept import UniversityDept
    from boac.models.university_dept_member import UniversityDeptMember
    depts = UniversityDept.query.all()
    for dept in depts:
        dept.delete_automated_members()
    std_commit(allow_test_environment=True)
    for dept in depts:
        for membership in dept.memberships_from_loch():
            # A non-numeric "uid" indicates a row from SIS advising tables best ignored.
            uid = membership['uid']
            if not re.match(r'^\d+$', uid):
                continue
            user = AuthorizedUser.find_by_uid(uid, ignore_deleted=False)
            is_coe = dept.dept_code == 'COENG'
            automate_degree_progress_permission = user.automate_degree_progress_permission if user else is_coe
            if user and not automate_degree_progress_permission:
                degree_progress_permission = user.degree_progress_permission
            else:
                degree_progress_permission = membership['degree_progress_permission']
            user = AuthorizedUser.create_or_restore(
                automate_degree_progress_permission=automate_degree_progress_permission,
                can_access_advising_data=membership['can_access_advising_data'],
                can_access_canvas_data=membership['can_access_canvas_data'],
                created_by='0',
                degree_progress_permission=degree_progress_permission,
                uid=uid,
            )
            if user:
                UniversityDeptMember.create_or_update_membership(
                    university_dept_id=dept.id,
                    authorized_user_id=user.id,
                    role='advisor',
                )
    DropInAdvisor.delete_orphans()
    SameDayAdvisor.delete_orphans()
    Scheduler.delete_orphans()


def load_filtered_cohort_counts():
    from boac.models.cohort_filter import CohortFilter
    from boac.models import json_cache
    json_cache.clear('cohort_filter_options_%')
    for cohort in CohortFilter.query.all():
        # Remove!
        cohort.clear_sids_and_student_count()
        cohort.update_alert_count(None)
        # Reload!
        cohort.to_api_json(include_students=False, include_alerts_for_user_id=cohort.owner_id)


def update_curated_group_lists():
    """Remove no-longer-accessible students from curated group lists."""
    from boac.models.curated_group import CuratedGroup
    for curated_group in CuratedGroup.query.all():
        all_sids = CuratedGroupStudent.get_sids(curated_group.id)
        available_students = [s['sid'] for s in data_loch.get_student_profiles(all_sids)]
        if len(all_sids) > len(available_students):
            unavailable_sids = set(all_sids) - set(available_students)
            app.logger.info(f'Deleting inaccessible SIDs from curated group {curated_group.id}: {unavailable_sids}')
            for sid in unavailable_sids:
                CuratedGroup.remove_student(curated_group.id, sid)
