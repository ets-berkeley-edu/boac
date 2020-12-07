"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.authorized_user import AuthorizedUser
import simplejson as json


def all_cohorts_owned_by(uid):
    def transform(c):
        return {
            'id': c.id,
            'name': c.name,
            'criteria': c.filter_criteria,
            'alertCount': c.alert_count,
            'totalStudentCount': c.student_count,
        }
    cohorts = sorted(AuthorizedUser.query.filter_by(uid=uid).first().cohort_filters, key=lambda c: c.name)
    return [transform(cohort) for cohort in cohorts]


def api_cohort_create(client, json_data=(), expected_status_code=200):
    response = client.post(
        '/api/cohort/create',
        data=json.dumps(json_data),
        content_type='application/json',
    )
    std_commit(allow_test_environment=True)
    assert response.status_code == expected_status_code
    return json.loads(response.data)


def api_cohort_get(client, cohort_id, expected_status_code=200):
    response = client.get(f'/api/cohort/{cohort_id}')
    assert response.status_code == expected_status_code
    return response.json


def api_cohort_events(client, cohort_id, expected_status_code=200):
    response = client.get(f'/api/cohort/{cohort_id}/events')
    assert response.status_code == expected_status_code
    return response.json


def api_curated_group_create(client, expected_status_code=200, name=None, sids=()):
    response = client.post(
        '/api/curated_group/create',
        data=json.dumps({
            'name': name,
            'sids': sids,
        }),
        content_type='application/json',
    )
    std_commit(allow_test_environment=True)
    assert response.status_code == expected_status_code
    return response.json


def api_curated_group_add_students(
        client,
        curated_group_id,
        expected_status_code=200,
        return_student_profiles=False,
        sids=(),
):
    response = client.post(
        '/api/curated_group/students/add',
        data=json.dumps({
            'curatedGroupId': curated_group_id,
            'returnStudentProfiles': return_student_profiles,
            'sids': sids,
        }),
        content_type='application/json',
    )
    std_commit(allow_test_environment=True)
    assert response.status_code == expected_status_code
    return response.json


def api_curated_group_remove_student(client, curated_group_id, sid, expected_status_code=200):
    response = client.delete(f'/api/curated_group/{curated_group_id}/remove_student/{sid}')
    std_commit(allow_test_environment=True)
    assert response.status_code == expected_status_code
    return response.json
