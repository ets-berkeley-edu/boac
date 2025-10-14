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

from flask import current_app as app
from flask import request

from boac.api.csv_file_download_utils import response_with_students_csv_download
from boac.api.decorators import advisor_required
from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import can_current_user_view_cohort, construct_phantom_cohort, is_unauthorized_domain, is_unauthorized_search
from boac.lib.util import get as get_param
from boac.lib.util import get_benchmarker
from boac.merged.sis_terms import current_term_id
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter


@app.route('/api/cohort_csv/download', methods=['POST'])
@advisor_required
def download_cohort_csv():
    benchmark = get_benchmarker('cohort download_csv')
    benchmark('begin')
    params = request.get_json()
    cohort_id = int(get_param(params, 'cohortId'))
    cohort = CohortFilter.find_by_id(cohort_id)
    cohort_owner_uid = AuthorizedUser.get_uid_per_id(cohort.owner_id)
    if cohort and can_current_user_view_cohort(cohort_owner_uid):
        sids = CohortFilter.get_sids(cohort.id)
        if len(sids) > app.config['COHORT_CSV_MAXIMUM_POPULATION']:
            raise BadRequestError(f"CSV maximum of {app.config['COHORT_CSV_MAXIMUM_POPULATION']} exceeded")
        fieldnames = get_param(params, 'csvColumnsSelected', [])
        term_id = get_param(params, 'termId') or current_term_id()
        return response_with_students_csv_download(
            benchmark=benchmark,
            domain=cohort.domain,
            fieldnames=fieldnames,
            sids=sids,
            term_id=term_id,
        )
    else:
        raise ResourceNotFoundError(f'No cohort found with identifier: {cohort_id}')


@app.route('/api/cohort_csv/download_per_filters', methods=['POST'])
@advisor_required
def download_csv_per_filters():
    benchmark = get_benchmarker('cohort download_csv_per_filters')
    benchmark('begin')
    params = request.get_json()
    filters = get_param(params, 'filters', [])
    fieldnames = get_param(params, 'csvColumnsSelected', [])
    domain = get_param(params, 'domain', 'default')
    term_id = get_param(params, 'termId') or current_term_id()

    if (domain == 'default' and not filters) or filters is None:
        raise BadRequestError('API requires \'filters\'')
    filter_keys = list(map(lambda f: f['key'], filters))
    if is_unauthorized_search(filter_keys):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    if is_unauthorized_domain(domain):
        raise ResourceNotFoundError(f'Domain \'{domain}\' is unavailable.')
    cohort = construct_phantom_cohort(
        domain=domain,
        filters=filters,
        offset=0,
        limit=None,
        include_profiles=False,
        include_sids=True,
        include_students=False,
    )
    if len(cohort['sids']) > app.config['COHORT_CSV_MAXIMUM_POPULATION']:
        raise BadRequestError(f"CSV maximum of {app.config['COHORT_CSV_MAXIMUM_POPULATION']} exceeded")
    return response_with_students_csv_download(
        benchmark=benchmark,
        domain=domain,
        fieldnames=fieldnames,
        sids=cohort['sids'],
        term_id=term_id,
    )
