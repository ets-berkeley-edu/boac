"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.lib.berkeley import ACADEMIC_STANDING_DESCRIPTIONS
from boac.lib.http import tolerant_jsonify
from boac.lib.util import process_input_from_rich_text_editor, to_bool_or_none
from boac.merged.sis_terms import current_term_id, current_term_name
from boac.models.degree_progress_category import degree_progress_category_type
from boac.models.degree_progress_course import ACCENT_COLOR_CODES
from boac.models.tool_setting import ToolSetting
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/config')
def app_config():
    return tolerant_jsonify({
        'academicStandingDescriptions': ACADEMIC_STANDING_DESCRIPTIONS,
        'apptDeskRefreshInterval': app.config['APPT_DESK_REFRESH_INTERVAL'],
        'boacEnv': app.config['BOAC_ENV'],
        'currentEnrollmentTerm': current_term_name(),
        'currentEnrollmentTermId': int(current_term_id()),
        'degreeCategoryTypeOptions': list(
            filter(
                lambda t: 'Placeholder' not in t and 'Campus' not in t, degree_progress_category_type.enums,
            ),
        ) + ['Campus Requirements'],
        'degreeProgressColorCodes': ACCENT_COLOR_CODES,
        'disableMatrixViewThreshold': app.config['DISABLE_MATRIX_VIEW_THRESHOLD'],
        'devAuthEnabled': app.config['DEVELOPER_AUTH_ENABLED'],
        'ebEnvironment': app.config['EB_ENVIRONMENT'] if 'EB_ENVIRONMENT' in app.config else None,
        'featureFlagAdmittedStudents': app.config['FEATURE_FLAG_ADMITTED_STUDENTS'],
        'featureFlagDegreeCheck': app.config['FEATURE_FLAG_DEGREE_CHECK'],
        'fixedWarningOnAllPages': app.config['FIXED_WARNING_ON_ALL_PAGES'],
        'googleAnalyticsId': app.config['GOOGLE_ANALYTICS_ID'],
        'isDemoModeAvailable': app.config['DEMO_MODE_AVAILABLE'],
        'maxAttachmentsPerNote': app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE'],
        'pingFrequency': app.config['PING_FREQUENCY'],
        'supportEmailAddress': app.config['BOAC_SUPPORT_EMAIL'],
        'timezone': app.config['TIMEZONE'],
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
    text = process_input_from_rich_text_editor(params.get('text', ''))
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
