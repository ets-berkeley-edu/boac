"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

from decimal import Decimal
import io

from boac.externals import data_loch
from boac.lib.mockingdata import MockRows, register_mock
import pytest


@pytest.mark.usefixtures('db_session')
class TestDataLoch:

    def test_get_advisor_uids_for_affiliations(self, app):
        """Returns one or more rows for each advisor in the program."""
        advisors = data_loch.get_advisor_uids_for_affiliations('UCOE', None)
        assert len(advisors)

        uids = [a['uid'] for a in advisors]
        advisors_by_uid = {uid: [a for a in advisors if a['uid'] == uid] for uid in uids}
        assert advisors_by_uid['13'] == [
            {
                'uid': '13',
                'can_access_advising_data': True,
                'can_access_canvas_data': False,
                'degree_progress_permission': 'read_write',
            },
        ]
        assert advisors_by_uid['90412'] == [
            {'uid': '90412', 'can_access_advising_data': False, 'can_access_canvas_data': False, 'degree_progress_permission': 'read'},
            {'uid': '90412', 'can_access_advising_data': True, 'can_access_canvas_data': True, 'degree_progress_permission': 'read'},
        ]
        assert advisors_by_uid['211159'] == [
            {
                'uid': '211159',
                'can_access_advising_data': True,
                'can_access_canvas_data': True,
                'degree_progress_permission': 'read_write',
            },
        ]
        assert advisors_by_uid['1022796'] == [
            {
                'uid': '1022796',
                'can_access_advising_data': False,
                'can_access_canvas_data': False,
                'degree_progress_permission': 'read_write',
            },
        ]

    def test_get_current_term_index(self):
        index = data_loch.get_current_term_index()
        assert index['current_term_name'] == 'Fall 2017'
        assert index['future_term_name'] == 'Spring 2018'

    def test_get_student_profiles(self):
        import json
        sid = '11667051'
        student_profiles = data_loch.get_student_profiles([sid])
        assert len(student_profiles) == 1

        student = student_profiles[0]
        assert student['sid'] == sid
        profile = json.loads(student['profile'])
        assert profile['demographics']['gender'] == 'Different Identity'
        assert profile['demographics']['underrepresented'] is False
        assert profile['sisProfile']['academicCareer'] == 'UGRD'

    def test_get_enrolled_primary_sections(self, app):
        sections = data_loch.get_enrolled_primary_sections('2178', 'MATH1')
        assert len(sections) == 6
        for section in sections:
            assert section['term_id'] == '2178'
            assert section['sis_course_name'].startswith('MATH 1')

    def test_get_term_gpas(self, app):
        term_gpas = data_loch.get_term_gpas(['11667051'])
        assert len(term_gpas) == 4
        assert term_gpas[0]['term_id'] == '2182'
        assert term_gpas[0]['sid'] == '11667051'
        assert term_gpas[0]['gpa'] == Decimal('2.900')
        assert term_gpas[0]['units_taken_for_gpa'] == 14
        assert term_gpas[3]['term_id'] == '2162'
        assert term_gpas[3]['sid'] == '11667051'
        assert term_gpas[3]['gpa'] == Decimal('3.800')
        assert term_gpas[3]['units_taken_for_gpa'] == 15

    def test_get_asc_advising_notes(self, app):
        notes = data_loch.get_asc_advising_notes('11667051')
        assert len(notes) == 2
        assert notes[0]['id'] == '11667051-139362'
        assert notes[0]['sid'] == '11667051'
        assert notes[0]['author_uid'] == '1133399'
        assert notes[0]['author_name'] == 'Lemmy Kilmister'
        assert notes[0]['subject'] is None
        assert notes[0]['body'] is None
        assert notes[0]['created_at']
        assert notes[0]['updated_at']
        assert notes[1]['author_name'] == 'Ginger Baker'
        assert notes[1]['subject'] == 'Ginger Baker\'s Air Force'
        assert notes[1]['body'] == 'Bands led by drummers tend to leave a lot of space for drum solos'

    def test_get_data_science_advising_notes(self):
        notes = data_loch.get_data_science_advising_notes('11667051')
        assert len(notes) == 2
        assert notes[0]['id'] == '11667051-20181003051208'
        assert notes[1]['id'] == '11667051-20190801112456'
        assert notes[1]['sid'] == '11667051'
        assert notes[1]['author_uid'] == '1133399'
        assert notes[1]['author_sid'] == '800700600'
        assert notes[1]['author_name'] == 'Joni Mitchell'
        assert notes[1]['advisor_email'] == 'joni@berkeley.edu'
        assert notes[1]['reason_for_appointment'] == 'Degree Check'
        assert notes[1]['note_body']
        assert notes[1]['created_at']

    def test_get_e_i_advising_notes(self, app):
        """Excludes notes with author name 'Reception Front Desk'."""
        notes = data_loch.get_e_i_advising_notes('11667051')
        assert len(notes) == 1
        assert notes[0]['id'] == '11667051-151620'
        assert notes[0]['sid'] == '11667051'
        assert notes[0]['author_uid'] == '1133398'
        assert notes[0]['author_name'] == 'Charlie Christian'
        assert notes[0]['created_at']
        assert notes[0]['updated_at']

    def test_get_e_i_advising_note_topics(self, app):
        topics = data_loch.get_e_i_advising_note_topics('11667051')
        assert len(topics) == 2
        assert topics[0]['id'] == '11667051-151620'
        assert topics[0]['topic'] == 'Course Planning'

    def test_get_admitted_student_by_sid(self, app):
        admit = data_loch.get_admitted_student_by_sid('00005852')
        assert admit['sid'] == '00005852'

    def test_get_sis_advising_note_attachment(self, app):
        attachment = data_loch.get_sis_advising_note_attachment('11667051', '11667051_00001_1.pdf')
        assert len(attachment) == 1
        assert attachment[0]['advising_note_id'] == '11667051-00001'
        assert attachment[0]['created_by'] == 'UCBCONVERSION'
        assert attachment[0]['sis_file_name'] == '11667051_00001_1.pdf'
        assert attachment[0]['user_file_name'] == 'efac7b10-c3f2-11e4-9bbd-ab6a6597d26f.pdf'

    def test_get_sis_advising_appointments(self, app):
        appointments = data_loch.get_sis_advising_appointments('11667051')
        assert len(appointments) == 3
        assert appointments[0]['id'] == '11667051-00010'
        assert appointments[1]['id'] == '11667051-00011'
        assert appointments[2]['id'] == '11667051-00012'

    def test_get_sis_late_drop_eforms(self):
        eforms = data_loch.get_sis_late_drop_eforms('11667051')
        assert len(eforms) == 3
        assert eforms[0]['id'] == 'eform-101'
        assert eforms[1]['id'] == 'eform-10099'
        assert eforms[2]['id'] == 'eform-10096'

    def test_get_students_ordering_default(self):
        o, o_secondary, o_tertiary, o_direction, supplemental_query_tables = data_loch.get_students_ordering(
            '2202',
        )
        assert o == "UPPER(regexp_replace(spi.last_name, '\\\\W', ''))"
        assert o_secondary == "UPPER(regexp_replace(spi.last_name, '\\\\W', ''))"
        assert o_tertiary == "UPPER(regexp_replace(spi.first_name, '\\\\W', ''))"
        assert o_direction == 'asc'
        assert supplemental_query_tables is None

    def test_get_students_ordering_gpa_ascending(self):
        o, o_secondary, o_tertiary, o_direction, supplemental_query_tables = data_loch.get_students_ordering(
            '2202',
            'gpa',
        )
        assert o == 'spi.gpa'
        assert o_secondary == "UPPER(regexp_replace(spi.last_name, '\\\\W', ''))"
        assert o_tertiary == "UPPER(regexp_replace(spi.first_name, '\\\\W', ''))"
        assert o_direction == 'asc'
        assert supplemental_query_tables is None

    def test_get_students_ordering_gpa_descending(self):
        o, o_secondary, o_tertiary, o_direction, supplemental_query_tables = data_loch.get_students_ordering(
            '2202',
            order_by='gpa desc',
        )
        assert o == 'spi.gpa'
        assert o_secondary == "UPPER(regexp_replace(spi.last_name, '\\\\W', ''))"
        assert o_tertiary == "UPPER(regexp_replace(spi.first_name, '\\\\W', ''))"
        assert o_direction == 'desc'
        assert supplemental_query_tables is None

    def test_get_students_ordering_units_in_progress_descending(self):
        o, o_secondary, o_tertiary, o_direction, supplemental_query_tables = data_loch.get_students_ordering(
            '2202',
            order_by='enrolled_units desc',
        )
        assert o == 'set.enrolled_units'
        assert o_secondary == "UPPER(regexp_replace(spi.last_name, '\\\\W', ''))"
        assert o_tertiary == "UPPER(regexp_replace(spi.first_name, '\\\\W', ''))"
        assert o_direction == 'desc'
        assert 'LEFT JOIN student.student_enrollment_terms set' in supplemental_query_tables
        assert 'ON set.sid = spi.sid AND set.term_id = \'2202\'' in supplemental_query_tables

    def test_get_students_ordering_term_gpa_descending(self):
        o, o_secondary, o_tertiary, o_direction, supplemental_query_tables = data_loch.get_students_ordering(
            '2202',
            order_by='term_gpa_2202 desc',
        )
        assert o == 'set.term_gpa'
        assert o_secondary == "UPPER(regexp_replace(spi.last_name, '\\\\W', ''))"
        assert o_tertiary == "UPPER(regexp_replace(spi.first_name, '\\\\W', ''))"
        assert o_direction == 'desc'
        assert 'LEFT JOIN student.student_enrollment_terms set' in supplemental_query_tables
        assert 'ON set.sid = spi.sid AND set.term_id = \'2202\'' in supplemental_query_tables

    def test_override_fixture(self, app):
        mr = MockRows(io.StringIO('sid,first_name,last_name\n20000000,Martin,Van Buren'))
        with register_mock(data_loch.get_sis_section_enrollments, mr):
            data = data_loch.get_sis_section_enrollments(2178, 12345)
        assert len(data) == 1
        assert {'sid': 20000000, 'first_name': 'Martin', 'last_name': 'Van Buren'} == data[0]

    def test_fixture_not_found(self, app):
        no_db = data_loch.get_sis_section_enrollments(0, 0)
        # TODO Real data_loch queries will return an empty list if the course is not found.
        assert no_db is None
