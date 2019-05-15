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
from boac.api.errors import BadRequestError
from boac.api.util import admin_required
from boac.lib.berkeley import sis_term_id_for_name
from boac.lib.http import tolerant_jsonify
from boac.lib.util import to_bool_or_none
from boac.models.tool_setting import ToolSetting
from flask import current_app as app, request
from flask_login import current_user


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
        'featureFlagEditNotes': app.config['FEATURE_FLAG_EDIT_NOTES'],
        'googleAnalyticsId': app.config['GOOGLE_ANALYTICS_ID'],
        'isDemoModeAvailable': app.config['DEMO_MODE_AVAILABLE'],
        'maxAttachmentsPerNote': app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE'],
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


@app.route('/api/service_announcement')
def get_service_announcement():
    if current_user.is_authenticated:
        announcement = _get_service_announcement()
        return tolerant_jsonify(announcement if current_user.is_admin or announcement['isPublished'] else None)
    else:
        return tolerant_jsonify(None)


@app.route('/api/service_announcement/update', methods=['POST'])
@admin_required
def update_service_announcement():
    params = request.get_json()
    text = params.get('text', '').strip()
    if not text and _is_service_announcement_published():
        raise BadRequestError('If the service announcement is published then API requires \'text\'')
    ToolSetting.upsert('SERVICE_ANNOUNCEMENT_TEXT', text)
    return tolerant_jsonify(_get_service_announcement())


@app.route('/api/service_announcement/publish', methods=['POST'])
@admin_required
def publish_service_announcement():
    publish = to_bool_or_none(request.get_json().get('publish'))
    if publish is None:
        raise BadRequestError('API requires \'publish\' arg')
    ToolSetting.upsert('SERVICE_ANNOUNCEMENT_IS_PUBLISHED', publish)
    return tolerant_jsonify(_get_service_announcement())


def load_json(relative_path):
    try:
        file = open(app.config['BASE_DIR'] + '/' + relative_path)
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None


def _get_service_announcement():
    return {
        'text': ToolSetting.get_tool_setting('SERVICE_ANNOUNCEMENT_TEXT'),
        'isPublished': _is_service_announcement_published(),
    }


def _is_service_announcement_published():
    is_published = ToolSetting.get_tool_setting('SERVICE_ANNOUNCEMENT_IS_PUBLISHED')
    return False if is_published is None else to_bool_or_none(is_published)
