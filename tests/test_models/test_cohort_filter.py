"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.errors import InternalServerError
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
import pytest
from tests.test_api.api_test_utils import all_cohorts_owned_by

asc_advisor_uid = '2040'
coe_advisor_uid = '1133399'


@pytest.mark.usefixtures('db_session')
class TestCohortFilter:
    """Cohort filter."""

    def test_filter_criteria(self):
        gpa_ranges = [
            {'min': 0, 'max': 1.999},
            {'min': 2, 'max': 2.499},
        ]
        group_codes = ['MFB-DB', 'MFB-DL']
        levels = ['Junior']
        majors = ['Environmental Economics & Policy', 'Gender and Women\'s Studies']
        unit_ranges = [
            'numrange(0, 5, \'[]\')',
            'numrange(30, NULL, \'[)\')',
        ]
        cohort = CohortFilter.create(
            uid='1022796',
            name='All criteria, all the time',
            filter_criteria={
                'gpaRanges': gpa_ranges,
                'groupCodes': group_codes,
                'inIntensiveCohort': None,
                'levels': levels,
                'majors': majors,
                'unitRanges': unit_ranges,
            },
        )
        cohort_id = cohort['id']
        cohort = CohortFilter.find_by_id(cohort_id)
        expected = {
            'gpaRanges': gpa_ranges,
            'groupCodes': group_codes,
            'inIntensiveCohort': None,
            'levels': levels,
            'majors': majors,
            'unitRanges': unit_ranges,
        }
        for key, value in expected.items():
            assert cohort['criteria'][key] == expected[key]
        assert cohort['totalStudentCount'] == len(CohortFilter.get_sids(cohort_id))

    def test_undefined_filter_criteria(self):
        with pytest.raises(InternalServerError):
            CohortFilter.create(
                uid=asc_advisor_uid,
                name='Cohort with undefined filter criteria',
                filter_criteria={
                    'genders': [],
                    'inIntensiveCohort': None,
                },
            )

    def test_create_and_delete_cohort(self):
        """Cohort_filter record to Flask-Login for recognized UID."""
        owner = AuthorizedUser.find_by_uid(asc_advisor_uid).uid
        shared_with = AuthorizedUser.find_by_uid(coe_advisor_uid).uid
        # Check validity of UIDs
        assert owner
        assert shared_with

        # Create and share cohort
        group_codes = ['MFB-DB', 'MFB-DL', 'MFB-MLB', 'MFB-OLB']
        cohort = CohortFilter.create(
            uid=owner,
            name='Football, Defense',
            filter_criteria={
                'groupCodes': group_codes,
            },
        )
        cohort_id = cohort['id']
        CohortFilter.share(cohort_id, shared_with)
        owners = CohortFilter.find_by_id(cohort_id)['owners']
        assert len(owners) == 2
        assert owner, shared_with in [user['uid'] for user in owners]
        assert cohort['totalStudentCount'] == len(CohortFilter.get_sids(cohort_id))

        # Delete cohort and verify
        previous_owner_count = cohort_count(owner)
        previous_shared_count = cohort_count(shared_with)
        CohortFilter.delete(cohort_id)
        assert cohort_count(owner) == previous_owner_count - 1
        assert cohort_count(shared_with) == previous_shared_count - 1

    def test_jsonify_cohort(self):
        """Can be JSONified."""
        cohorts = AuthorizedUser.find_by_uid(coe_advisor_uid).cohort_filters
        assert len(cohorts)
        expected_name = 'Roberta\'s Students'
        cohort = next((c for c in cohorts if c.name == expected_name), None)
        assert cohort
        assert cohort.to_api_json()['name'] == expected_name


def cohort_count(user_uid):
    return len(all_cohorts_owned_by(user_uid))
