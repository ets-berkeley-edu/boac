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

import io

from boac.externals import data_loch
from boac.lib.mockingdata import MockRows, register_mock
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
        assert section['meetings'][0]['days'] == 'Mon, Tue, Wed, Thu, Fri'
        assert section['meetings'][0]['instructors'] == ['George Orwell']
        assert section['meetings'][0]['time'] == '12:00 pm - 12:59 pm'
        assert section['meetings'][0]['location'] == 'Wheeler 999'

    def test_handles_multiple_locations_and_instructors(self, app):
        section = get_sis_section('2178', 90200)
        assert section['meetings'][0]['days'] == 'Tue, Thu'
        assert section['meetings'][0]['time'] == '6:00 pm - 6:59 pm'
        assert section['meetings'][0]['location'] == 'Dwinelle 117'
        assert section['meetings'][0]['instructors'] == ['Johan Huizinga', 'Ernst Robert Curtius']
        assert section['meetings'][1]['days'] == 'Wednesday'
        assert section['meetings'][1]['time'] == '1:30 pm - 2:59 pm'
        assert section['meetings'][1]['location'] == 'Campbell Hall 501B'
        assert section['meetings'][1]['instructors'] == ['Johan Huizinga', 'Ernst Robert Curtius']

    def test_handles_eap_courses(self, app):
        section_id = 98000
        rows = [
            'sis_term_id,sis_section_id,sis_course_title,sis_course_name,is_primary,sis_instruction_format,'
            'instruction_mode,sis_section_num,allowed_units,instructor_uid,instructor_name,instructor_role_code,'
            'meeting_location,meeting_days,meeting_start_time,meeting_end_time,meeting_start_date,meeting_end_date',
            '2178,98000,Rabelais en Indre-et-Loire,EAPFRENCH 1998,true,LEC,001,22.0,'
            ',,,,,,,2017-08-23 00:00:00 UTC,2017-12-08 00:00:00 UTC',
        ]
        mr = MockRows(io.StringIO('\n'.join(rows)))
        with register_mock(data_loch.get_sis_section, mr):
            section = get_sis_section('2178', section_id)
            assert section['sectionId'] == section_id
            assert section['displayName'] == 'EAPFRENCH 1998'
            assert section['title'] == 'Rabelais en Indre-et-Loire'
            assert section['units'] is None
            assert section['meetings'][0]['days'] is None
            assert section['meetings'][0]['time'] is None
            assert section['meetings'][0]['location'] is None
            assert section['meetings'][0]['instructors'] == []

    def test_handles_online_courses(self, app):
        section_id = 99000
        rows = [
            'sis_term_id,sis_section_id,sis_course_title,sis_course_name,is_primary,sis_instruction_format,'
            'instruction_mode,sis_section_num,allowed_units,instructor_uid,instructor_name,instructor_role_code,'
            'meeting_location,meeting_days,meeting_start_time,meeting_end_time,meeting_start_date,meeting_end_date',
            '2178,99000,MedXieval Dead,MED ST 1999,true,ONL,H,001,86.0,'
            '9922330,Hal Colossus,PI,,,,,2017-08-23 00:00:00 UTC,2017-12-08 00:00:00 UTC',
            # Also include an empty instructor row, since they sometimes show up.
            '2178,99000,MedXieval Dead,MED ST 1999,true,ONL,P,001,86.0,'
            '9922330,,APRX,,,,,2017-08-23 00:00:00 UTC,2017-12-08 00:00:00 UTC',
        ]
        mr = MockRows(io.StringIO('\n'.join(rows)))
        with register_mock(data_loch.get_sis_section, mr):
            section = get_sis_section('2178', section_id)
            assert section['sectionId'] == section_id
            assert section['displayName'] == 'MED ST 1999'
            assert section['title'] == 'MedXieval Dead'
            assert section['units'] == 86
            assert section['meetings'][0]['days'] is None
            assert section['meetings'][0]['time'] is None
            assert section['meetings'][0]['location'] is None
            assert section['meetings'][0]['instructors'] == ['Hal Colossus']
