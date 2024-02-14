"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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
import os
import sys

from boac.lib import scriptify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


@scriptify.in_app
def main(app):
    from boac import std_commit
    from boac.models.cohort_filter import CohortFilter

    legacy_key = 'advisorLdapUids'
    coe_key = 'coeAdvisorLdapUids'

    for cohort in CohortFilter.query.all():
        if coe_key not in cohort.filter_criteria:
            # Replace legacy with COE key
            criteria = cohort.filter_criteria
            if not isinstance(criteria, dict):
                criteria = json.loads(cohort.filter_criteria)
            criteria[coe_key] = criteria.pop(legacy_key, None)
            # Update db
            cohort.filter_criteria = json.dumps(criteria)
            std_commit()
            print(f'Cohort {cohort.id} updated to have {coe_key}: {criteria[coe_key]}')


main()
