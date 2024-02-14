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

from boac.models.note import Note
from boac.models.topic import Topic
from sqlalchemy import and_

admin_uid = '2040'
coe_advisor_uid = '1133399'
coe_advisor_no_advising_data_uid = '1022796'
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
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_all_topics(client)
        topics = _get_topic_labels(api_json)
        assert 'Topic for notes, 1' in topics
        assert 'Topic for notes, 9' in topics
        assert 'Topic for notes, deleted' not in topics
        assert topics[-1] == 'Other / Reason not listed'

    def test_get_all_topics(self, client, fake_auth):
        """Get all note topic options, not including deleted."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_all_topics(client, include_deleted=True)
        topics = _get_topic_labels(api_json)
        assert 'Topic for notes, 1' in topics
        assert 'Topic for notes, 9' in topics
        assert 'Topic for notes, deleted' in topics
        assert topics[-1] == 'Other / Reason not listed'


class TestCreateTopic:

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        _api_create_topic(client, topic='Foo', expected_status_code=401)

    def test_deny_non_admin_user(self, client, fake_auth):
        """Denies access to non-admin user."""
        fake_auth.login(l_s_college_advisor_uid)
        _api_create_topic(client, topic='Foo', expected_status_code=401)

    def test_invalid_arguments(self, client, fake_auth):
        """Fails due to invalid arguments."""
        fake_auth.login(admin_uid)
        _api_create_topic(
            client,
            topic=' ',
            expected_status_code=400,
        )

    def test_create_topic(self, client, fake_auth):
        """Admin user can create a topic."""
        fake_auth.login(admin_uid)
        topic = 'A valid topic'
        api_json = _api_create_topic(client, topic=topic)
        assert api_json['id']
        assert api_json['topic'] == topic
        assert api_json['deletedAt'] is None


class TestDeleteTopic:

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        assert client.delete(f'/api/topic/delete/{_get_sample_topic().id}').status_code == 401

    def test_deny_non_admin_user(self, client, fake_auth):
        """Denies access to non-admin user."""
        fake_auth.login(l_s_college_advisor_uid)
        assert client.delete(f'/api/topic/delete/{_get_sample_topic().id}').status_code == 401

    def test_delete_topic(self, client, fake_auth):
        """Admin users can delete topics."""
        fake_auth.login(admin_uid)
        topic_label = 'Delete me, Seymour!'
        topic = _api_create_topic(client, topic_label)
        topic_id = topic['id']
        assert topic['deletedAt'] is None
        assert client.delete(f'/api/topic/delete/{topic_id}').status_code == 200

        def _get_topic():
            api_json = _topics_for_notes(client, include_deleted=True)
            topic_json = next((row for row in api_json if row['id'] == topic_id), None)
            assert topic_json
            return topic_json

        topic = _get_topic()
        assert topic['topic'] == topic_label
        assert topic['deletedAt']
        # Lastly, undelete.
        _undelete_topic(client, topic_id)
        assert _get_topic()['deletedAt'] is None


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

    def test_get_all_topics_including_deleted(self, client, fake_auth):
        """Get all note topic options, including deleted."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_all_note_topics(client, include_deleted=True)
        topics = _get_topic_labels(api_json)
        for index in range(10):
            assert f'Topic for notes, {index}' in topics
        assert 'Topic for notes, deleted' in topics
        assert topics[-1] == 'Other / Reason not listed'

    def test_get_all_topics(self, client, fake_auth):
        """Get all note topic options, not including deleted."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_all_note_topics(client)
        topics = _get_topic_labels(api_json)
        for index in range(10):
            assert f'Topic for notes, {index}' in topics
        assert 'Topic for notes, deleted' not in topics
        assert topics[-1] == 'Other / Reason not listed'


class TestTopicUsageStatistics:

    @classmethod
    def _api_usage_statistics(cls, client, expected_status_code=200):
        response = client.get('/api/topics/usage_statistics')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Deny anonymous access."""
        self._api_usage_statistics(client, expected_status_code=401)

    def test_deny_non_admin_user(self, client, fake_auth):
        """Denies access to non-admin user."""
        fake_auth.login(l_s_college_advisor_uid)
        self._api_usage_statistics(client, expected_status_code=401)

    def test_get_topic_usage_statistics(self, client, fake_auth, mock_advising_note):
        """Admin user can get topic usage report."""
        fake_auth.login(admin_uid)
        api_json = self._api_usage_statistics(client)
        assert list(api_json.keys()) == ['notes']
        assert len(api_json['notes'])
        # Verify counts
        all_notes = Note.query.filter(Note.deleted_at == None).all()  # noqa: E711
        all_notes = [a.to_api_json() for a in all_notes]
        for topic_id, count in api_json['notes'].items():
            topic = Topic.find_by_id(topic_id)
            matches = list(filter(lambda a: topic.topic in a['topics'], all_notes))
            assert len(matches) == count


def _api_create_topic(
        client,
        topic,
        expected_status_code=200,
):
    data = {
        'topic': topic,
    }
    response = client.post(
        '/api/topic/create',
        data=json.dumps(data),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


def _get_sample_topic():
    topic = Topic.query.filter(and_(Topic.id == 1, Topic.deleted_at == None)).first()  # noqa: E711
    assert topic
    return topic


def _get_topic_labels(api_json):
    return [row['topic'] for row in api_json]


def _topics_for_notes(client, include_deleted=None, expected_status_code=200):
    api_path = '/api/topics/for_notes'
    api_path += f'?includeDeleted={str(include_deleted).lower()}' if include_deleted else ''
    response = client.get(api_path)
    assert response.status_code == expected_status_code
    return response.json


def _undelete_topic(client, topic_id, expected_status_code=200):
    response = client.post(
        '/api/topic/undelete',
        data=json.dumps({'id': topic_id}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json
