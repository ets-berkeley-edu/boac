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

from boac.lib.cohort_filter_definition import get_cohort_filter_definitions, get_cohort_filter_options, translate_cohort_filter
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param
from boac.merged.student import get_student_query_scope
from flask import current_app as app, request
from flask_login import login_required


@app.route('/api/menu/cohort/deprecated_filter_definitions')
@login_required
def get_filter_definitions():
    # TODO: Deprecated. Remove when Vue-cutover is complete.
    categories = get_cohort_filter_definitions(get_student_query_scope())
    for category in categories:
        for definition in category:
            if definition['type'] == 'array':
                for index, option in enumerate(definition['options']):
                    option['position'] = index
    return tolerant_jsonify(categories)


@app.route('/api/menu/cohort/all_filter_options', methods=['POST'])
@login_required
def all_cohort_filter_options():
    existing_filters = get_param(request.get_json(), 'existingFilters', [])
    return tolerant_jsonify(get_cohort_filter_options(existing_filters))


@app.route('/api/menu/cohort/translate_filter_criteria_to_menu', methods=['POST'])
@login_required
def translate_cohort_filter_to_menu():
    criteria = get_param(request.get_json(), 'filterCriteria')
    return tolerant_jsonify(translate_cohort_filter(criteria))
