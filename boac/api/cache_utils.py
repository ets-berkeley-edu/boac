"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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


from threading import Thread

from boac import db, std_commit
from boac.externals import data_loch
from boac.lib import berkeley
from boac.models import json_cache
from boac.models.alert import Alert
from boac.models.curated_group import CuratedGroupStudent
from boac.models.job_progress import JobProgress
from boac.models.json_cache import JsonCache
from flask import current_app as app
from sqlalchemy import and_, or_


def refresh_request_handler(term_id, load_only=False):
    """Handle a start refresh admin request by returning an error status or starting the job on a background thread."""
    job_state = JobProgress().get()
    if job_state is None or (not job_state['start']) or job_state['end']:
        job_type = 'Load' if load_only else 'Refresh'
        JobProgress().start({
            'job_type': job_type,
            'term_id': term_id,
        })
        app.logger.warn('About to start background thread')
        thread = Thread(
            target=background_thread_refresh,
            daemon=True,
            kwargs={
                'app_arg': app._get_current_object(),
                'term_id': term_id,
                'job_type': job_type,
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


def background_thread_refresh(app_arg, term_id, job_type, continuation=False):
    with app_arg.app_context():
        try:
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
    # TODO Currently we're not looping anything into the staging table, so we expect refresh count to be zero.
    # If a more considered set of cache entries comes back into the loop, this error message should come back
    # too.
    # if refresh_count == 0:
    #     JobProgress().update('ERROR: No cache entries copied from staging')
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

    JobProgress().update(f'About to refresh alerts for term {term_id}')
    refresh_alerts(term_id)

    if term_id == berkeley.current_term_id():
        JobProgress().update(f'About to load filtered cohort counts')
        load_filtered_cohort_counts()
        JobProgress().update(f'About to update curated group memberships')
        update_curated_group_lists()


def refresh_alerts(term_id):
    Alert.deactivate_all_for_term(term_id)
    Alert.update_all_for_term(term_id)


def load_filtered_cohort_counts():
    from boac.models.cohort_filter import CohortFilter
    for cohort in CohortFilter.query.all():
        # Remove!
        cohort.update_student_count(None)
        cohort.update_alert_count(None)
        # The db schema supports multiple cohort owners but in the real world it is one owner per cohort.
        owner_id = cohort.owners[0].id if len(cohort.owners) else None
        # Reload!
        cohort.to_api_json(include_students=False, include_alerts_for_user_id=owner_id)


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
