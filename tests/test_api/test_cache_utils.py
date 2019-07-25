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

import datetime

from boac import std_commit
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.curated_group import CuratedGroup, CuratedGroupStudent
from boac.models.db_relationships import UniversityDeptMember
from boac.models.university_dept import UniversityDept
import pytest
from tests.test_api.api_test_utils import all_cohorts_owned_by


@pytest.mark.usefixtures('db_session')
class TestCacheUtils:
    """Test cache utils."""

    def test_creates_alert_for_midterm_grade(self, app):
        from boac.api.cache_utils import refresh_alerts
        refresh_alerts(2178)
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')
        assert 1 == len(alerts)
        assert 0 < alerts[0]['id']
        assert 'midterm' == alerts[0]['alertType']
        assert '2178_90100' == alerts[0]['key']
        assert 'BURMESE 1A midterm grade of D+.' == alerts[0]['message']

    def test_update_curated_group_lists(self, app):
        from boac.api.cache_utils import update_curated_group_lists
        curated_group = CuratedGroup.create(
            owner_id=AuthorizedUser.find_by_uid('6446').id,
            name='This group has one student not in Data Loch',
        )
        original_sids = ['3456789012', '5678901234', '7890123456']
        for sid in original_sids:
            CuratedGroup.add_student(curated_group.id, sid)
        sid_not_in_data_loch = '19040616'
        CuratedGroup.add_student(curated_group.id, sid_not_in_data_loch)
        std_commit(allow_test_environment=True)

        revised_sids = CuratedGroupStudent.get_sids(curated_group.id)
        assert sid_not_in_data_loch in revised_sids
        update_curated_group_lists()
        std_commit(allow_test_environment=True)

        final_sids = CuratedGroupStudent.get_sids(curated_group.id)
        assert sid_not_in_data_loch not in final_sids
        assert set(final_sids) == set(original_sids)

    def test_load_filtered_cohort_counts(self, app):
        from boac.api.cache_utils import load_filtered_cohort_counts
        uid = '2040'
        cohorts = all_cohorts_owned_by(uid)
        assert len(cohorts)
        for cohort in cohorts:
            assert cohort['alertCount'] is None
        load_filtered_cohort_counts()
        for cohort in all_cohorts_owned_by('2040'):
            assert cohort['alertCount'] >= 0


class TestRefreshDepartmentMemberships:
    """Test department membership refresh."""

    def test_adds_coe_advisors(self, app):
        """Adds COE advisors newly found in the loch."""
        AuthorizedUser.query.filter_by(uid='1022796').delete()
        std_commit(allow_test_environment=True)

        dept_coe = UniversityDept.query.filter_by(dept_code='COENG').first()
        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users) == 3
        assert next((u for u in coe_users if u.uid == '1022796'), None) is None

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users) == 4
        assert next(u for u in coe_users if u.uid == '1022796')
        assert AuthorizedUser.query.filter_by(uid='1022796').first().deleted_at is None

    def test_restores_coe_advisors(self, app):
        """Restores previously deleted COE advisors found in the loch."""
        deleted_user = AuthorizedUser.query.filter_by(uid='1022796').first()
        deleted_user.deleted_at = datetime.datetime.now()
        UniversityDeptMember.query.filter_by(authorized_user_id=deleted_user.id).delete()
        std_commit(allow_test_environment=True)

        dept_coe = UniversityDept.query.filter_by(dept_code='COENG').first()
        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users) == 3
        assert next((u for u in coe_users if u.uid == '1022796'), None) is None

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users) == 4
        assert next(u for u in coe_users if u.uid == '1022796')
        assert AuthorizedUser.query.filter_by(uid='1022796').first().deleted_at is None

    def test_removes_coe_advisors(self, app):
        """Removes COE advisors not found in the loch."""
        dept_coe = UniversityDept.query.filter_by(dept_code='COENG').first()
        bad_user = AuthorizedUser.create_or_restore(uid='666')
        UniversityDeptMember.create_membership(dept_coe, bad_user, is_advisor=True, is_director=False)
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users) == 5
        assert next(u for u in coe_users if u.uid == '666')
        assert AuthorizedUser.query.filter_by(uid='666').first().deleted_at is None

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users) == 4
        assert next((u for u in coe_users if u.uid == '666'), None) is None
        assert AuthorizedUser.query.filter_by(uid='666').first().deleted_at
