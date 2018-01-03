from functools import wraps
from boac.api import cache_utils
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
    term_id = request.args.get('term') or cache_utils.current_term_id()
    return term_id


@app.route('/api/admin/cachejob')
@admin_required
def get_cachejob_status():
    progress = JobProgress().get()
    return tolerant_jsonify({
        'progress': progress,
    })


@app.route('/api/admin/cachejob/clear')
@admin_required
def clear_cachejob():
    progress = JobProgress().delete()
    return tolerant_jsonify({
        'progressDeleted': progress,
    })


@app.route('/api/admin/cachejob/load')
@admin_required
def start_load_only():
    """This endpoint lets us load still-uncached data without having to erase any data which was already cached.
    """
    job_state = cache_utils.refresh_request_handler(term(), load_only=True)
    return tolerant_jsonify(job_state)


@app.route('/api/admin/cachejob/refresh')
@admin_required
def start_refresh():
    return tolerant_jsonify(cache_utils.refresh_request_handler(term()))
