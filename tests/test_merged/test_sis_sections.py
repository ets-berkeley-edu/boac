"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


from boac.merged.sis_sections import get_sis_section
import pytest


@pytest.mark.usefixtures('db_session')
class TestGetSisSection:

    def test_get_section(self, app):
        section_id = 90100
        section = get_sis_section('2178', section_id)
        assert section['sectionId'] == section_id
        assert section['displayName'] == 'BURMESE 1A'
        assert section['title'] == 'Introductory Burmese'
        assert section['units'] == 4
        assert section['meetings'][0]['days'] == 'M, T, W, Th, F'
        assert section['meetings'][0]['instructors'] == ['George Orwell']
        assert section['meetings'][0]['time'] == '12:00 pm - 12:59 pm'
        assert section['meetings'][0]['location'] == 'Wheeler 999'

    def test_handles_multiple_locations_and_instructors(self, app):
        section = get_sis_section('2178', 90200)
        assert section['meetings'][0]['days'] == 'T, Th'
        assert section['meetings'][0]['time'] == '6:00 pm - 6:59 pm'
        assert section['meetings'][0]['location'] == 'Dwinelle 117'
        assert section['meetings'][0]['instructors'] == ['Johan Huizinga', 'Ernst Robert Curtius']
        assert section['meetings'][1]['days'] == 'Wednesday'
        assert section['meetings'][1]['time'] == '1:30 pm - 2:59 pm'
        assert section['meetings'][1]['location'] == 'Campbell Hall 501B'
        assert section['meetings'][1]['instructors'] == ['Johan Huizinga', 'Ernst Robert Curtius']
