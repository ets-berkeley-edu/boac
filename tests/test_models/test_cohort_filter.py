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

from boac import std_commit
from boac.api.errors import InternalServerError
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
import pytest
from tests.test_api.api_test_utils import all_cohorts_owned_by

asc_advisor_uid = '2040'
coe_advisor_uid = '1133399'
ce3_advisor_uid = '2525'


@pytest.mark.usefixtures('db_session')
class TestCohortFilter:
    """Cohort filter."""

    def test_filter_criteria(self):
        gpa_ranges = [
            {'min': 0, 'max': 1.999},
            {'min': 2, 'max': 2.499},
        ]
        group_codes = ['MFB-DB', 'MFB-DL']
        intended_majors = ['Public Health BA']
        levels = ['Junior']
        majors = ['Environmental Economics & Policy', 'Gender and Women\'s Studies']
        minors = ['Physics UG']
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
                'intendedMajors': intended_majors,
                'levels': levels,
                'majors': majors,
                'minors': minors,
                'unitRanges': unit_ranges,
            },
        )
        cohort_id = cohort['id']
        cohort = CohortFilter.find_by_id(cohort_id)
        expected = {
            'gpaRanges': gpa_ranges,
            'groupCodes': group_codes,
            'inIntensiveCohort': None,
            'intendedMajors': intended_majors,
            'levels': levels,
            'majors': majors,
            'minors': minors,
            'unitRanges': unit_ranges,
        }
        for key, value in expected.items():
            assert cohort['criteria'][key] == expected[key]
        assert cohort['totalStudentCount'] == len(CohortFilter.get_sids(cohort_id))

    def test_ce3_filter_criteria(self):
        colleges = ['College of Letters and Science', 'College of Engineering']
        family_dependent_ranges = [
            {'min': 0, 'max': 2},
            {'min': 5, 'max': 5},
        ]
        freshman_or_transfer = ['Transfer']
        has_fee_waiver = True
        cohort = CohortFilter.create(
            uid=ce3_advisor_uid,
            name='All my admits',
            filter_criteria={
                'colleges': colleges,
                'familyDependentRanges': family_dependent_ranges,
                'freshmanOrTransfer': freshman_or_transfer,
                'hasFeeWaiver': has_fee_waiver,
            },
            domain='admitted_students',
        )
        cohort_id = cohort['id']
        cohort = CohortFilter.find_by_id(cohort_id)
        expected = {
            'colleges': colleges,
            'familyDependentRanges': family_dependent_ranges,
            'freshmanOrTransfer': freshman_or_transfer,
            'hasFeeWaiver': has_fee_waiver,
        }
        for key, value in expected.items():
            assert cohort['criteria'][key] == expected[key]
        assert cohort['totalStudentCount'] == len(CohortFilter.get_sids(cohort_id))
        assert cohort['students']

    def test_undefined_filter_criteria(self):
        with pytest.raises(InternalServerError):
            CohortFilter.create(
                uid=asc_advisor_uid,
                name='Cohort with undefined filter criteria',
                filter_criteria={
                    'inIntensiveCohort': None,
                },
            )

    def test_create_and_delete_cohort(self):
        """Cohort_filter record to Flask-Login for recognized UID."""
        owner = AuthorizedUser.find_by_uid(asc_advisor_uid).uid
        # Check validity of UID
        assert owner

        # Create cohort
        group_codes = ['MFB-DB', 'MFB-DL', 'MFB-MLB', 'MFB-OLB']
        cohort = CohortFilter.create(
            uid=owner,
            name='Football, Defense',
            filter_criteria={
                'groupCodes': group_codes,
            },
        )
        cohort_id = cohort['id']
        assert CohortFilter.find_by_id(cohort_id)['owner']['uid'] == owner
        assert cohort['totalStudentCount'] == len(CohortFilter.get_sids(cohort_id))

        # Delete cohort and verify
        previous_owner_count = cohort_count(owner)
        CohortFilter.delete(cohort_id)
        std_commit(allow_test_environment=True)
        assert cohort_count(owner) == previous_owner_count - 1

    def test_jsonify_cohort(self):
        """Can be JSONified."""
        cohorts = AuthorizedUser.find_by_uid(coe_advisor_uid).cohort_filters
        assert len(cohorts)
        expected_name = 'Roberta\'s Students'
        cohort = next((c for c in cohorts if c.name == expected_name), None)
        assert cohort
        assert cohort.to_api_json()['name'] == expected_name

        admit_cohorts = AuthorizedUser.find_by_uid(ce3_advisor_uid).cohort_filters
        assert len(admit_cohorts)
        expected_name = 'First Generation Students'
        admit_cohort = next((c for c in admit_cohorts if c.name == expected_name), None)
        assert admit_cohort
        assert admit_cohort.to_api_json()['name'] == expected_name


def cohort_count(user_uid):
    return len(all_cohorts_owned_by(user_uid))
