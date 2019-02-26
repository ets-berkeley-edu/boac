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

import json

from boac import __version__ as version
from boac.lib.berkeley import sis_term_id_for_name
from boac.lib.http import tolerant_jsonify
from flask import current_app as app


@app.route('/api/config')
def app_config():
    current_term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
    current_term_id = sis_term_id_for_name(current_term_name)
    return tolerant_jsonify({
        'boacEnv': app.config['BOAC_ENV'],
        'currentEnrollmentTerm': current_term_name,
        'currentEnrollmentTermId': int(current_term_id),
        'disableMatrixViewThreshold': app.config['DISABLE_MATRIX_VIEW_THRESHOLD'],
        'devAuthEnabled': app.config['DEVELOPER_AUTH_ENABLED'],
        'ebEnvironment': app.config['EB_ENVIRONMENT'] if 'EB_ENVIRONMENT' in app.config else None,
        'featureFlagCreateNotes': app.config['FEATURE_FLAG_CREATE_NOTES'],
        'googleAnalyticsId': app.config['GOOGLE_ANALYTICS_ID'],
        'supportEmailAddress': app.config['BOAC_SUPPORT_EMAIL'],
    })


@app.route('/api/version')
def app_version():
    v = {
        'version': version,
    }
    build_stats = load_json('config/build-summary.json')
    if build_stats:
        v.update(build_stats)
    else:
        v.update({
            'build': None,
        })
    return tolerant_jsonify(v)


def load_json(relative_path):
    try:
        file = open(app.config['BASE_DIR'] + '/' + relative_path)
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None
