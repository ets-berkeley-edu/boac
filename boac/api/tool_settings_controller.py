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

from boac.api.util import admin_required
from boac.lib.http import tolerant_jsonify
from boac.models.tool_setting import ToolSetting
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/tool_settings', methods=['POST'])
@login_required
def get_tool_settings():
    params = request.get_json()
    api_json = {}
    keys = params.get('keys')
    if isinstance(keys, list) and len(keys):
        settings = ToolSetting.get_tool_settings(keys)
        if settings:
            for setting in settings:
                if setting.is_public or current_user.is_admin:
                    api_json.update(setting.to_api_json())
    return tolerant_jsonify(api_json)


@app.route('/api/tool_setting/upsert', methods=['POST'])
@admin_required
def upsert_tool_setting():
    params = request.get_json()
    key = params.get('key')
    value = params.get('value')
    # NOTE: The 'is_public' property cannot be modified via API
    return tolerant_jsonify(ToolSetting.upsert(key, value).to_api_json())
