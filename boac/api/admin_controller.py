from functools import wraps
from boac.api import cache_utils
from boac.lib import berkeley
from boac.lib.http import tolerant_jsonify
from boac.merged import import_asc_athletes
from boac.models.job_progress import JobProgress
from flask import current_app as app, request
from flask_login import current_user


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        auth_key = app.config['API_KEY']
        login_ok = current_user.is_authenticated and current_user.is_admin
        api_key_ok = auth_key and (request.headers.get('App-Key') == auth_key)
        if login_ok or api_key_ok:
            return func(*args, **kw)
        else:
            app.logger.warn(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_required


def term():
    term_id = request.args.get('term') or berkeley.current_term_id()
    return term_id


@app.route('/api/admin/asc_import')
@admin_required
def do_import_from_asc():
    status = import_asc_athletes.update_from_asc_api()
    return tolerant_jsonify(status)


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
    """Lets us load still-uncached data without having to erase any data which was already cached."""
    job_state = cache_utils.refresh_request_handler(term(), load_only=True)
    return tolerant_jsonify(job_state)


@app.route('/api/admin/cachejob/refresh')
@admin_required
def start_refresh():
    return tolerant_jsonify(cache_utils.refresh_request_handler(term()))


@app.route('/api/admin/cachejob/import_refresh')
@admin_required
def start_import_refresh():
    return tolerant_jsonify(cache_utils.refresh_request_handler(term(), import_asc=True))
