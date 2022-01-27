"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.curated_group import CuratedGroup, CuratedGroupStudent
from boac.models.university_dept import UniversityDept
from boac.models.university_dept_member import UniversityDeptMember
import pytest
from tests.test_api.api_test_utils import all_cohorts_owned_by


coe_advisor_uid = '1022796'


@pytest.mark.usefixtures('db_session')
class TestCacheUtils:

    def test_creates_alert_for_midterm_grade(self, app):
        from boac.api.cache_utils import refresh_alerts
        refresh_alerts(2178)
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')
        alert = next((a for a in alerts if a['alertType'] == 'midterm'), None)
        assert alert
        assert 'midterm' == alert['alertType']
        assert '2178_90100' == alert['key']
        assert 'BURMESE 1A midpoint deficient grade of D+.' == alert['message']

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

    def test_load_filtered_cohort_counts(self, admin_user_uid, app):
        from boac.api.cache_utils import load_filtered_cohort_counts
        cohorts = all_cohorts_owned_by(admin_user_uid)
        assert len(cohorts)
        for cohort in cohorts:
            assert cohort['alertCount'] is None
        load_filtered_cohort_counts()
        for cohort in all_cohorts_owned_by('2040'):
            assert cohort['alertCount'] >= 0


class TestRefreshCalnetAttributes:

    def test_removes_and_restores(self, app):
        from boac.api.cache_utils import refresh_calnet_attributes
        from boac.models import json_cache
        from boac.models.json_cache import JsonCache
        removed_advisor = coe_advisor_uid
        removed_ldap_record = '2040'
        all_active_uids = {u.uid for u in AuthorizedUser.get_all_active_users()}
        assert {removed_advisor, removed_ldap_record}.issubset(all_active_uids)
        calnet_filter = JsonCache.key.like('calnet_user_%')
        all_cached_uids = {r.json['uid'] for r in JsonCache.query.filter(calnet_filter).all()}
        assert {removed_advisor, removed_ldap_record}.issubset(all_cached_uids)
        AuthorizedUser.query.filter_by(uid=removed_advisor).delete()
        JsonCache.query.filter_by(key=f'calnet_user_for_uid_{removed_ldap_record}').delete()
        std_commit(allow_test_environment=True)

        refresh_calnet_attributes()
        assert json_cache.fetch(f'calnet_user_for_uid_{removed_ldap_record}') is not None
        assert json_cache.fetch(f'calnet_user_for_uid_{removed_advisor}') is None


class TestRefreshCurrentTermIndex:
    """Test current term index refresh."""

    def test_refresh_current_term_index(self, app):
        """Deletes existing index from the cache and adds a fresh one."""
        from boac.api.cache_utils import refresh_current_term_index
        from boac.models import json_cache
        from boac.models.json_cache import JsonCache

        index_row = JsonCache.query.filter_by(key='current_term_index').first()
        index_row.json = 'old'
        json_cache.update_jsonb_row(index_row)
        index = json_cache.fetch('current_term_index')
        assert(index) == 'old'

        refresh_current_term_index()

        index = json_cache.fetch('current_term_index')
        assert(index['current_term_name']) == 'Fall 2017'
        assert(index['future_term_name']) == 'Spring 2018'


class TestRefreshDepartmentMemberships:

    def test_adds_coe_advisors(self, app):
        """Adds COE advisors newly found in the loch."""
        # Note: You will not find this UID in development_db (test data setup). It is seeded in loch.sql test data.
        coe_uid = '1234567'
        if AuthorizedUser.find_by_uid(coe_uid):
            AuthorizedUser.query.filter_by(uid=coe_uid).delete()
        std_commit(allow_test_environment=True)

        dept_coe = UniversityDept.query.filter_by(dept_code='COENG').first()
        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users)
        assert next((u for u in coe_users if u.uid == coe_uid), None) is None

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert next((u for u in coe_users if u.uid == coe_uid), None)
        user = AuthorizedUser.query.filter_by(uid=coe_uid).first()
        assert user.can_access_canvas_data is False
        assert user.can_access_advising_data is False
        assert user.degree_progress_permission == 'read'
        assert user.deleted_at is None
        assert user.created_by == '0'
        assert user.department_memberships[0].automate_membership is True

    def test_restores_coe_advisors(self, user_factory):
        """Restores previously deleted COE advisors found in the loch."""
        from boac.api.cache_utils import refresh_department_memberships

        coe_advisor = user_factory(
            dept_codes=['COENG', 'QCADV'],
        )
        uid = coe_advisor.uid
        user_id = coe_advisor.id
        AuthorizedUser.delete(uid=uid)
        UniversityDeptMember.query.filter_by(authorized_user_id=user_id).delete()
        std_commit(allow_test_environment=True)

        dept_coe = UniversityDept.find_by_dept_code(dept_code='COENG')
        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        coe_user_count = len(coe_users)
        assert coe_user_count
        assert next((u for u in coe_users if u.uid == uid), None) is None

        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert next(u for u in coe_users if u.uid == uid)

        user = AuthorizedUser.find_by_uid(uid=uid, ignore_deleted=False)
        std_commit(allow_test_environment=True)
        assert user.can_access_canvas_data is True
        assert user.can_access_advising_data is True
        # Verify that degree_progress_permission persists
        assert user.automate_degree_progress_permission is True
        # TODO: Fix BOAC-4629 ("users with multiple depts lose DP access")
        # assert user.degree_progress_permission == 'read_write'
        assert user.deleted_at is None
        assert user.created_by == '0'
        assert user.department_memberships[0].automate_membership is True

    def test_removes_coe_advisors(self, app):
        """Removes COE advisors not found in the loch."""
        dept_coe = UniversityDept.query.filter_by(dept_code='COENG').first()
        bad_user = AuthorizedUser.create_or_restore(uid='666', created_by='2040')
        UniversityDeptMember.create_or_update_membership(
            dept_coe.id,
            bad_user.id,
            role='advisor',
        )
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        coe_user_count = len(coe_users)
        assert coe_user_count
        assert next(u for u in coe_users if u.uid == '666')
        assert AuthorizedUser.query.filter_by(uid='666').first().deleted_at is None

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users) == coe_user_count - 1
        assert next((u for u in coe_users if u.uid == '666'), None) is None
        assert AuthorizedUser.query.filter_by(uid='666').first().deleted_at

    def test_respects_automate_memberships_flag(self, app, db):
        dept_coe = UniversityDept.query.filter_by(dept_code='COENG').first()
        manually_added_user = AuthorizedUser.create_or_restore(
            uid='1024',
            created_by='2040',
            degree_progress_permission='read_write',
        )
        manual_membership = UniversityDeptMember.create_or_update_membership(
            dept_coe.id,
            manually_added_user.id,
            role='advisor',
            automate_membership=False,
        )

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        coe_user_count = len(coe_users)
        assert coe_user_count
        assert next(u for u in coe_users if u.uid == '1024')
        user = AuthorizedUser.find_by_uid(uid='1024')
        assert user
        assert user.degree_progress_permission == 'read_write'

        manual_membership.automate_membership = True
        db.session.add(manual_membership)
        std_commit(allow_test_environment=True)

        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        coe_users = [au.authorized_user for au in dept_coe.authorized_users]
        assert len(coe_users) == coe_user_count - 1
        assert next((u for u in coe_users if u.uid == '1024'), None) is None
        assert not AuthorizedUser.find_by_uid(uid='1024')

    def test_replaces_non_automated_user_with_automated_user(self, app, db):
        authorized_user_id = AuthorizedUser.query.filter_by(uid='1133397').first().id
        memberships = UniversityDeptMember.query.filter_by(authorized_user_id=authorized_user_id).all()
        assert len(memberships) == 1
        memberships[0].automate_membership = False
        memberships[0].authorized_user.created_by = '2040'
        std_commit(allow_test_environment=True)

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        memberships = UniversityDeptMember.query.filter_by(authorized_user_id=authorized_user_id).all()
        assert len(memberships) == 1
        assert memberships[0].automate_membership is True
        assert memberships[0].authorized_user.created_by == '0'

    def test_adds_l_s_advisors(self):
        """Adds L&S minor advisors who have no other affiliations to the correct dept."""
        AuthorizedUser.query.filter_by(uid='1133397').delete()
        std_commit(allow_test_environment=True)

        dept_ucls = UniversityDept.query.filter_by(dept_code='QCADVMAJ').first()
        ucls_users = [au.authorized_user for au in dept_ucls.authorized_users]
        ucls_user_count = len(ucls_users)
        assert next((u for u in ucls_users if u.uid == '1133397'), None) is None

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        ucls_users = [au.authorized_user for au in dept_ucls.authorized_users]
        assert len(ucls_users) == ucls_user_count + 1
        assert next(u for u in ucls_users if u.uid == '1133397')
        assert AuthorizedUser.query.filter_by(uid='1133397').first().deleted_at is None

    def test_adds_non_advisors_to_other_group(self):
        from boac.api.cache_utils import refresh_department_memberships

        dept = UniversityDept.query.filter_by(dept_code='ZZZZZ').first()
        refresh_department_memberships()
        std_commit(allow_test_environment=True)
        users = [au.authorized_user for au in dept.authorized_users]
        assert users[0].can_access_canvas_data is False
        assert users[0].degree_progress_permission is None

    def test_allows_advisor_to_change_departments(self):
        """Updates membership for a former CoE advisor who switches to L&S."""
        user = AuthorizedUser.find_by_uid('242881')
        dept_coe = UniversityDept.query.filter_by(dept_code='COENG').first()
        UniversityDeptMember.create_or_update_membership(
            dept_coe.id,
            user.id,
            role='advisor',
        )
        dept_ucls = UniversityDept.query.filter_by(dept_code='QCADVMAJ').first()
        UniversityDeptMember.delete_membership(dept_ucls.id, user.id)
        std_commit(allow_test_environment=True)

        ucls_users = [au.authorized_user for au in dept_ucls.authorized_users]
        ucls_user_count = len(ucls_users)

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        ucls_users = [au.authorized_user for au in dept_ucls.authorized_users]
        assert len(ucls_users) == ucls_user_count + 1
        assert next(u for u in ucls_users if u.uid == '242881')
        updated_user = AuthorizedUser.query.filter_by(uid='242881').first()
        assert updated_user.deleted_at is None
        assert updated_user.created_by == '0'
        assert updated_user.department_memberships[0].university_dept_id == dept_ucls.id

    def test_deletes_drop_in_advisor_orphans(self):
        """Cleans up drop-in advisor record for a department membership that no longer exists."""
        from boac.models.authorized_user_extension import DropInAdvisor
        dept_ucls = UniversityDept.query.filter_by(dept_code='QCADVMAJ').first()
        bad_user = AuthorizedUser.create_or_restore(uid='666', created_by='2040')
        UniversityDeptMember.create_or_update_membership(
            dept_ucls.id,
            bad_user.id,
            role='advisor',
        )
        DropInAdvisor.create_or_update_membership(dept_ucls.dept_code, bad_user.id)
        std_commit(allow_test_environment=True)

        ucls_drop_in_advisors = DropInAdvisor.advisors_for_dept_code(dept_ucls.dept_code)
        assert len(ucls_drop_in_advisors) == 2
        assert bad_user.id in [d.authorized_user_id for d in ucls_drop_in_advisors]

        from boac.api.cache_utils import refresh_department_memberships
        refresh_department_memberships()
        std_commit(allow_test_environment=True)

        ucls_drop_in_advisors = DropInAdvisor.advisors_for_dept_code(dept_ucls.dept_code)
        assert len(ucls_drop_in_advisors) == 1
