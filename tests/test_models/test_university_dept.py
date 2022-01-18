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

from boac.models.university_dept import UniversityDept


class TestUniversityDept:
    """University Departments."""

    def test_memberships_from_loch(self):
        """Aggregates role and privilege data from the loch for each of its members."""
        dept_coe = UniversityDept.query.filter_by(dept_code='COENG').first()
        advisors = dept_coe.memberships_from_loch()
        assert len(advisors)
        uids = [a['uid'] for a in advisors]
        advisors_by_uid = {
            uid: [a for a in advisors if a['uid'] == uid] for uid in uids}
        assert advisors_by_uid.get('13') == [
            {
                'uid': '13',
                'can_access_advising_data': True,
                'can_access_canvas_data': False,
                'degree_progress_permission': 'read_write',
            },
        ]
        assert advisors_by_uid.get('90412') == [
            {
                'uid': '90412',
                'can_access_advising_data': True,
                'can_access_canvas_data': True,
                'degree_progress_permission': 'read',
            },
        ]
        assert advisors_by_uid.get('1022796') == [
            {
                'uid': '1022796',
                'can_access_advising_data': False,
                'can_access_canvas_data': False,
                'degree_progress_permission': 'read_write',
            },
        ]
        assert advisors_by_uid.get('1133399') == [
            {
                'uid': '1133399',
                'can_access_advising_data': True,
                'can_access_canvas_data': True,
                'degree_progress_permission': 'read_write',
            },
        ]
        assert advisors_by_uid.get('211159') == [
            {
                'uid': '211159',
                'can_access_advising_data': True,
                'can_access_canvas_data': True,
                'degree_progress_permission': 'read_write',
            },
        ]
