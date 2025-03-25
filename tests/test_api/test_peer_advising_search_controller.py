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

from boac.models.peer_advising_department import PeerAdvisingDepartment
import simplejson as json

ce3_navcal_peer_advisor_uid = '1133400'


class TestPeerAdvisingNoteSearch:
    """Peer Advising Notes search API."""

    @classmethod
    def _assert(cls, api_json, note_count=0, note_ids=()):
        assert 'notes' in api_json
        notes = api_json['notes']
        assert len(notes) == note_count
        for idx, note_id in enumerate(note_ids):
            assert notes[idx].get('id') == note_id

    def test_peer_advising_search_with_missing_input_no_options(self, client, fake_auth):
        """Notes search is nothing without any input."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        _api_search(client, ' \t  ', peer_advising_department_id=navcal_department.id, expected_status_code=400)

    def test_peer_advising_search_includes_notes_if_requested(self, client, fake_auth):
        """Does not include any notes if the notes do not exist."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        api_json = _api_search(client, 'Brigitte', peer_advising_department_id=navcal_department.id)
        self._assert(api_json, note_count=0)


def _api_search(
        client,
        phrase,
        peer_advising_department_id,
        expected_status_code=200,
):
    response = client.post(
        '/api/peer_advising/notes/search',
        content_type='application/json',
        data=json.dumps({
            'searchPhrase': phrase,
            'peerAdvisingDeptId': peer_advising_department_id,
        }),
    )

    assert response.status_code == expected_status_code
    return response.json
