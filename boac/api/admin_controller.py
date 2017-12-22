from functools import wraps
from boac.api import cache_utils
from boac.lib import berkeley
from boac.lib.http import tolerant_jsonify
from boac.models.job_progress import JobProgress
from flask import current_app as app, request
from flask_login import current_user


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        if (not current_user.is_authenticated) or (not current_user.is_admin):
            return app.login_manager.unauthorized()
        return func(*args, **kw)
    return _admin_required


def term():
    term_id = request.args.get('term') or berkeley.sis_term_id_for_name(app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])
    return term_id


@app.route('/api/admin/refresh')
@admin_required
def get_refresh_status():
    progress = JobProgress().get()
    return tolerant_jsonify({
        'progress': progress,
    })


@app.route('/api/admin/refresh/clear')
@admin_required
def clear_refresh():
    progress = JobProgress().delete()
    return tolerant_jsonify({
        'progressDeleted': progress,
    })


@app.route('/api/admin/refresh/load')
@admin_required
def start_load_only():
    """If a refresh has been interrupted (due to server restart, for example), this endpoint lets us continue
    to load new data without having to erase any data which was successfully cached.
    """
    job_state = cache_utils.refresh_request_handler(term(), load_only=True)
    return tolerant_jsonify(job_state)


@app.route('/api/admin/refresh/start')
@admin_required
def start_refresh():
    return tolerant_jsonify(cache_utils.refresh_request_handler(term()))
