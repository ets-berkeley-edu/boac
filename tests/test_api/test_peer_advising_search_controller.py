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

import simplejson as json

from boac.models.peer_advising_department import PeerAdvisingDepartment

admin_uid = '2040'
ce3_navcal_peer_advisor_uid = '1133400'
ce3_pam_advisor_uid = '2525'
ce3_non_pam_advisor_uid = '5405613'
coe_mech_peer_advisor_uid = '1913062'
eop_peer_advisor_uid = '1563405'


class TestPeerAdvisingNoteSearch:
    """Peer Advising Notes search API."""

    @classmethod
    def _assert(cls, api_json, note_count=0, student_count=0, note_ids=()):
        assert 'notes' in api_json
        notes = api_json['notes']
        students = api_json['students']
        assert len(notes) == note_count
        assert len(students) == student_count
        for idx, note_id in enumerate(note_ids):
            assert notes[idx].get('id') == note_id

    def test_peer_advising_search_with_missing_input_no_options(self, client, fake_auth):
        """Notes search is nothing without any input."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        _api_search(client, ' \t  ', peer_advising_department_id=navcal_department.id, expected_status_code=400)

    def test_peer_advising_search_notes_no_notes(self, client, fake_auth):
        """Does not include any notes if the notes do not exist."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'Anastasia', peer_advising_department_id=navcal_department.id)
        self._assert(api_json, note_count=0, student_count=0)

    def test_peer_advising_search_notes_no_match(
            self,
            client,
            fake_auth,
            mock_navcal_peer_advising_note,  # noqa: ARG002
            mock_navcal_peer_advising_note_with_comments,  # noqa: ARG002
        ):
        """Does not include any notes if none match the search query."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'Brigitte', peer_advising_department_id=navcal_department.id)
        self._assert(api_json, note_count=0, student_count=0)

    def test_peer_advising_search_includes_peer_notes(
            self,
            client,
            fake_auth,
            mock_navcal_peer_advising_note,  # noqa: ARG002
            mock_navcal_peer_advising_note_with_comments,  # noqa: ARG002
        ):
        """Includes notes created by other peer advisors in the same department."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'Anastasia', peer_advising_department_id=navcal_department.id)
        self._assert(api_json, note_count=1, student_count=0)

        api_json = _api_search(client, 'a comment', peer_advising_department_id=navcal_department.id)
        self._assert(api_json, note_count=1, student_count=0)

    def test_peer_advising_search_includes_pam_notes(self, client, fake_auth, mock_navcal_peer_advising_manager_note):  # noqa: ARG002
        """Includes notes created by a Peer Advisor Manager in the same department."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'daisy', peer_advising_department_id=navcal_department.id)
        self._assert(api_json, note_count=1, student_count=0)

    def test_search_excludes_foreign_dept_peer_notes(
            self,
            client,
            fake_auth,
            mock_navcal_peer_advising_note,  # noqa: ARG002
            mock_navcal_peer_advising_note_with_comments,  # noqa: ARG002
        ):
        """Does not include notes or comments created by peer advisors outside the department."""
        fake_auth.login(eop_peer_advisor_uid)
        eop_department = PeerAdvisingDepartment.get_department_by_name('Educational Opportunity Program')
        api_json = _api_search(client, 'Anastasia', peer_advising_department_id=eop_department.id)
        self._assert(api_json, note_count=0, student_count=0)

        api_json = _api_search(client, 'comment', peer_advising_department_id=eop_department.id)
        self._assert(api_json, note_count=0, student_count=0)

    def test_excludes_foreign_dept_pam_notes(self, client, fake_auth, mock_navcal_peer_advising_manager_note):  # noqa: ARG002
        """Does not include a note created by Peer Advisor Manager outside the department."""
        fake_auth.login(eop_peer_advisor_uid)
        eop_department = PeerAdvisingDepartment.get_department_by_name('Educational Opportunity Program')
        api_json = _api_search(client, 'daisy', peer_advising_department_id=eop_department.id)
        self._assert(api_json, note_count=0, student_count=0)

    def test_search_excludes_same_dept_non_pam_note(self, client, fake_auth, mock_ce3_advising_note):  # noqa: ARG002
        """Does not include a note created bxy a non-PAM advisor in the same department."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'darling', peer_advising_department_id=navcal_department.id)
        self._assert(api_json, note_count=0, student_count=0)

        fake_auth.login(eop_peer_advisor_uid)
        eop_department = PeerAdvisingDepartment.get_department_by_name('Educational Opportunity Program')
        api_json = _api_search(client, 'darling', peer_advising_department_id=eop_department.id)
        self._assert(api_json, note_count=0, student_count=0)

    def test_search_excludes_pam_comment_foreign_dept_peer_note(
            self,
            client,
            fake_auth,
            mock_navcal_peer_advising_note_with_comments,  # noqa: ARG002
        ):
        """Does not include a peer advising note from a different department and commented on by Peer Advisor Manager in the same department."""
        fake_auth.login(coe_mech_peer_advisor_uid)
        mech_eng_department = PeerAdvisingDepartment.get_department_by_name('Mechanical Engineering')
        api_json = _api_search(client, 'a comment', peer_advising_department_id=mech_eng_department.id)
        self._assert(api_json, note_count=0, student_count=0)

    def test_search_excludes_pam_comment_non_peer_note(
            self,
            client,
            fake_auth,
            mock_advising_note_with_comments,  # noqa: ARG002
        ):
        """Does not include a non-peer note commented on by a Peer Advisor Manager in the same department."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'a comment', peer_advising_department_id=navcal_department.id)
        self._assert(api_json, note_count=0, student_count=0)

    def test_peer_advisor_student_search_excludes_gpa(self, client, fake_auth):
        """Strips GPA data from the student feed for peer advisors."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'debaser@berkeley.edu', peer_advising_department_id=navcal_department.id, notes=False)
        students = api_json['students']
        assert len(students) == 1
        assert students[0]['lastName'] == 'Doolittle'
        assert 'cumulativeGPA' not in students[0]
        assert 'termGpa' not in students[0]

    def test_admin_student_search_includes_gpa(self, client, fake_auth):
        """Does not strip GPA data from the student feed for admins/regular advisors."""
        fake_auth.login(admin_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'debaser@berkeley.edu', peer_advising_department_id=navcal_department.id, notes=False)
        students = api_json['students']
        assert len(students) == 1
        assert students[0]['lastName'] == 'Doolittle'
        assert students[0]['cumulativeGPA'] == 3.495
        assert 'termGpa' in students[0]

    def test_strip_gpa_removes_nested_term_gpa(self, app):  # noqa: ARG002
        """Strips termGpa when it is nested within a student's 'term' element as well as top-level."""
        from boac.api.search_controller import _strip_gpa
        students = [
            {
                'cumulativeGPA': 3.495,
                'lastName': 'Doolittle',
                'term': {
                    'termGpa': {'gpa': 1.8, 'unitsTakenForGpa': 15.0},
                    'termId': '2178',
                },
                'termGpa': [{'gpa': 3.5, 'termId': '2172'}],
            },
        ]
        stripped = _strip_gpa(students)
        assert len(stripped) == 1
        student = stripped[0]
        assert 'cumulativeGPA' not in student
        assert 'termGpa' not in student
        assert 'termGpa' not in student['term']
        # Non-GPA data in the nested 'term' element is preserved.
        assert student['term']['termId'] == '2178'


def _api_search(
        client,
        phrase,
        peer_advising_department_id,
        expected_status_code=200,
        notes=True,
        students=True,
):
    response = client.post(
        '/api/search/peer_advising_notes',
        content_type='application/json',
        data=json.dumps({
            'searchPhrase': phrase,
            'peerAdvisingDepartmentId': peer_advising_department_id,
            'notes': notes,
            'students': students,
        }),
    )

    assert response.status_code == expected_status_code
    return response.json
