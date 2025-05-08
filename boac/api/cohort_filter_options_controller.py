"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.decorators import advisor_required
from boac.api.errors import ResourceNotFoundError
from boac.api.util import is_unauthorized_domain
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param
from boac.merged.cohort_filter_options import CohortFilterOptions
from flask import current_app as app, request


@app.route('/api/cohort_filter_options', methods=['POST'])
@advisor_required
def all_cohort_filter_options():
    params = request.get_json()
    existing_filters = get_param(params, 'existingFilters', [])
    domain = get_param(params, 'domain', 'default')
    owner_uid = get_param(params, 'ownerUid')
    if is_unauthorized_domain(domain):
        raise ResourceNotFoundError(f'Domain \'{domain}\' is unavailable.')
    return tolerant_jsonify(
        CohortFilterOptions.get_cohort_filter_option_groups(
            domain=domain,
            owner_uid=owner_uid,
            existing_filters=existing_filters,
        ),
    )


@app.route('/api/cohort_filter_options/translate', methods=['POST'])
@advisor_required
def translate_cohort_filter_to_menu():
    params = request.get_json()
    domain = get_param(params, 'domain', 'default')
    owner_uid = get_param(params, 'ownerUid')
    if is_unauthorized_domain(domain):
        raise ResourceNotFoundError(f'Domain \'{domain}\' is unavailable.')
    criteria = get_param(params, 'criteria')
    filter_options = CohortFilterOptions.translate_to_filter_options(owner_uid, domain, criteria)
    return tolerant_jsonify(filter_options)
