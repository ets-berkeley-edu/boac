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

from tests.util import override_config

coe_drop_in_advisor_uid = '1133399'
coe_advisor_no_advising_data_uid = '1022796'
coe_scheduler_uid = '6972201'
l_s_college_advisor_uid = '188242'


class TestGetTopics:

    @classmethod
    def _api_all_topics(cls, client, include_deleted=False, expected_status_code=200):
        api_path = '/api/topics/all'
        if include_deleted is not None:
            api_path += f'?includeDeleted={str(include_deleted).lower()}'
        response = client.get(api_path)
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        self._api_all_topics(client, expected_status_code=401)

    def test_user_without_advising_data_access(self, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_all_topics(client, expected_status_code=401)

    def test_not_include_deleted(self, client, fake_auth):
        """Get all topics, including deleted."""
        fake_auth.login(coe_drop_in_advisor_uid)
        api_json = self._api_all_topics(client)
        assert 'Topic for all, 1' in api_json
        assert 'Topic for appointments, 2' in api_json
        assert 'Topic for notes, 9' in api_json
        assert 'Topic for appointments, deleted' not in api_json
        assert 'Topic for notes, deleted' not in api_json
        assert api_json[-1] == 'Other / Reason not listed'

    def test_get_all_topics(self, client, fake_auth):
        """Get all note topic options, not including deleted."""
        fake_auth.login(coe_drop_in_advisor_uid)
        api_json = self._api_all_topics(client, include_deleted=True)
        assert 'Topic for all, 1' in api_json
        assert 'Topic for notes, 9' in api_json
        assert 'Topic for appointments, 2' in api_json
        assert 'Topic for appointments, deleted' in api_json
        assert 'Topic for notes, deleted' in api_json
        assert api_json[-1] == 'Other / Reason not listed'


class TestTopicsForAppointment:

    @classmethod
    def _get_topics(cls, client, include_deleted=None, expected_status_code=200):
        api_path = '/api/topics/for_appointments'
        if include_deleted is not None:
            api_path += f'?includeDeleted={str(include_deleted).lower()}'
        response = client.get(api_path)
        assert response.status_code == expected_status_code
        return response.json

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._get_topics(client, expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            self._get_topics(client, expected_status_code=401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is not a drop-in advisor."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            self._get_topics(client, expected_status_code=401)

    def test_dept_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's dept is not configured for drop-in advising."""
        fake_auth.login(coe_scheduler_uid)
        self._get_topics(client, expected_status_code=401)

    def test_scheduler_get_appointment_topics(self, app, client, fake_auth):
        """COE scheduler can get topics."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            topics = self._get_topics(client)
            assert len(topics) == 9
            assert topics[-1] == 'Other / Reason not listed'

    def test_advisor_get_appointment_topics(self, app, client, fake_auth):
        """COE advisor can get topics."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_drop_in_advisor_uid)
            topics = self._get_topics(client)
            assert len(topics) == 9
            assert topics[-1] == 'Other / Reason not listed'

    def test_get_all_topics_including_deleted(self, app, client, fake_auth):
        """Get all appointment topic options, including deleted."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_drop_in_advisor_uid)
            topics = self._get_topics(client, include_deleted=True)
            assert len(topics) == 11
            assert 'Topic for appointments, deleted' in topics
            assert topics[-1] == 'Other / Reason not listed'


class TestTopicsForNotes:

    @classmethod
    def _api_all_note_topics(cls, client, include_deleted=None, expected_status_code=200):
        api_path = '/api/topics/for_notes'
        if include_deleted is not None:
            api_path += f'?includeDeleted={str(include_deleted).lower()}'
        response = client.get(api_path)
        assert response.status_code == expected_status_code
        return response.json

    def test_get_all_topics_not_authenticated(self, client):
        """Deny anonymous access to note topics."""
        self._api_all_note_topics(client, expected_status_code=401)

    def test_user_without_advising_data_access(self, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_all_note_topics(client, expected_status_code=401)

    def test_get_all_topics_for_notes_including_deleted(self, client, fake_auth):
        """Get all note topic options, including deleted."""
        fake_auth.login(coe_drop_in_advisor_uid)
        api_json = self._api_all_note_topics(client, include_deleted=True)
        assert 'Topic for all, 1' in api_json
        assert 'Topic for notes, 9' in api_json
        assert 'Topic for notes, deleted' in api_json
        assert api_json[-1] == 'Other / Reason not listed'

    def test_get_all_topics_for_notes(self, client, fake_auth):
        """Get all note topic options, not including deleted."""
        fake_auth.login(coe_drop_in_advisor_uid)
        api_json = self._api_all_note_topics(client)
        assert 'Topic for all, 1' in api_json
        assert 'Topic for notes, 9' in api_json
        assert 'Topic for notes, deleted' not in api_json
        assert api_json[-1] == 'Other / Reason not listed'
