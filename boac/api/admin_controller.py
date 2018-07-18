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


from boac.api import cache_utils
from boac.api.util import admin_required
from boac.lib import berkeley
from boac.lib.http import tolerant_jsonify
from boac.models.job_progress import JobProgress
from flask import current_app as app, request


def term():
    term_id = request.args.get('term') or berkeley.current_term_id()
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


@app.route('/api/admin/cachejob/continue')
@admin_required
def start_continuation_of_interrupted_job():
    return tolerant_jsonify(cache_utils.continue_request_handler())


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
# For the moment, keeping this around as a legacy alias for start_refresh.
@admin_required
def start_import_refresh():
    return tolerant_jsonify(cache_utils.refresh_request_handler(term()))
