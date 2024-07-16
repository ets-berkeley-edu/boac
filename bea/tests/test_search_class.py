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

from bea.config.bea_test_config import BEATestConfig
from bea.test_utils import utils
import pytest

test = BEATestConfig()
test.search_class()
current_term = utils.get_current_term()
test_searches = []
for student in test.test_students:
    for term in student.enrollment_data.enrollment_terms():
        if student.enrollment_data.term_name(term) == current_term.name:
            for course in student.enrollment_data.courses(term):
                course_code = student.enrollment_data.sis_course_data(course)['code']
                section = student.enrollment_data.course_primary_section(course)
                section_num = student.enrollment_data.sis_section_data(section)['number']

                subject_area, separator, catalog_id = course_code.rpartition(' ')
                abbreviated_subject_area = subject_area[0:-2]
                strings = [course_code, f'{abbreviated_subject_area} {catalog_id}']

                if len(catalog_id) > 1:
                    strings.append(catalog_id)
                for string in strings:
                    test_searches.append({
                        'course_code': course_code,
                        'section_num': section_num,
                        'search_string': string,
                    })


@pytest.mark.usefixtures('page_objects')
class TestSearchClasses:

    def test_login(self):
        self.homepage.dev_auth(test.advisor)

    @pytest.mark.parametrize('search', test_searches,
                             ids=[test_search['search_string'] for test_search in test_searches])
    def test_search_class(self, search):
        self.homepage.enter_simple_search_and_hit_enter(search['search_string'])
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_class_in_search_result(search['course_code'], search['section_num'])

    def test_search_result_link(self):
        test_case = test_searches[0]
        code = test_case['course_code']
        num = test_case['section_num']

        self.homepage.enter_simple_search_and_hit_enter(test_case['search_string'])
        self.homepage.wait_for_spinner()
        if self.search_results_page.is_class_in_search_result(code, num):
            self.search_results_page.click_class_result(code, num)
            self.class_page.wait_for_boa_title(code)
