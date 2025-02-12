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

from bea.config.bea_test_config import BEATestConfig
from bea.models.degree_progress.degree_check_perms import DegreeCheckPerms
from bea.models.degree_progress.degree_check_template import DegreeCheckTemplate
from bea.test_utils import boa_degree_progress_utils
from bea.test_utils import utils
import pytest
from selenium.webdriver.common.by import By

test = BEATestConfig()
test.degree_check()
template = next(filter(lambda t: 'Templates' in t.name, test.degree_templates))

cat_1 = template.categories[0]
cat_2 = template.categories[1]

sub_cat_1 = cat_1.sub_categories[0]
sub_cat_2 = cat_2.sub_categories[0]

cat_1_course_1 = cat_1.course_reqts[0]
sub_cat_1_course_1 = sub_cat_1.course_reqts[0]
sub_cat_1_course_2 = sub_cat_1.course_reqts[1]


@pytest.mark.usefixtures('page_objects')
class TestTemplateCreation:

    def test_set_advisor_perms(self):
        self.homepage.load_page()
        self.homepage.dev_auth()
        self.pax_manifest_page.load_page()
        self.pax_manifest_page.set_deg_prog_perm(test.advisor, test.dept, DegreeCheckPerms.WRITE)
        self.pax_manifest_page.set_deg_prog_perm(test.advisor_read_only, test.dept, DegreeCheckPerms.READ)

    def test_advisor_login(self):
        self.pax_manifest_page.log_out()
        self.homepage.dev_auth(test.advisor)

    def test_degree_template_name_required(self):
        self.homepage.click_degree_checks()
        self.degree_template_mgmt_page.click_create_degree()
        assert not self.degree_template_mgmt_page.is_degree_save_enabled()

    def test_degree_template_name_max_255_chars(self):
        name = template.name * 20
        self.degree_template_mgmt_page.enter_degree_name(name)
        utils.assert_equivalence(self.degree_template_mgmt_page.degree_name_input_value(), name[0:255])

    def test_save_redirects_to_empty_template(self):
        self.degree_template_mgmt_page.enter_degree_name(template.name)
        self.degree_template_mgmt_page.click_save_new_degree()
        self.degree_template_page.when_present(self.degree_template_page.template_heading(template),
                                               utils.get_short_timeout())
        boa_degree_progress_utils.set_new_template_id(template)

    def test_new_template_in_list_of_templates(self):
        self.degree_template_page.click_degree_checks()
        self.degree_template_mgmt_page.wait_for_degree_link(template)

    def test_new_template_creation_date(self):
        utils.assert_equivalence(self.degree_template_mgmt_page.degree_check_create_date(template),
                                 template.created_date)

    def test_degree_template_unique_name_required(self):
        self.degree_template_mgmt_page.click_create_degree()
        self.degree_template_mgmt_page.enter_degree_name(template.name)
        self.degree_template_mgmt_page.click_save_new_degree()
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.DUPE_NAME_MSG,
                                                    utils.get_short_timeout())


@pytest.mark.usefixtures('page_objects')
class TestUnitRequirements:

    def test_load_template(self):
        self.degree_template_mgmt_page.click_degree_checks()
        self.degree_template_mgmt_page.click_degree_link(template)

    def test_unit_reqt_creation_name_required(self):
        self.degree_template_page.click_add_unit_reqt()
        self.degree_template_page.when_present(self.degree_template_page.UNIT_REQT_NAME_INPUT, 1)
        assert not self.degree_template_page.is_unit_reqt_create_enabled()

    def test_unit_reqt_creation_name_max_255_chars(self):
        name = template.unit_reqts[0].name * 20
        self.degree_template_page.enter_unit_reqt_name(name)
        utils.assert_equivalence(self.degree_template_page.unit_reqt_name_input_value(), name[0:255])

    def test_unit_reqt_creation_unit_count_required(self):
        assert not self.degree_template_page.is_unit_reqt_create_enabled()

    def test_unit_reqt_creation_cancel(self):
        self.degree_template_page.click_cancel_unit_reqt()
        self.degree_template_page.when_present(self.degree_template_page.UNIT_REQTS_EMPTY_MSG, 1)

    def test_unit_reqt_creation(self):
        for reqt in template.unit_reqts:
            self.degree_template_page.create_unit_reqt(reqt, template)

    def test_unit_reqt_creation_name_saved(self):
        for reqt in template.unit_reqts:
            utils.assert_equivalence(self.degree_template_page.visible_unit_reqt_name(reqt), reqt.name)

    def test_unit_reqt_creation_unit_count_saved(self):
        for reqt in template.unit_reqts:
            utils.assert_equivalence(self.degree_template_page.visible_unit_reqt_num(reqt), reqt.unit_count)

    def test_unit_reqt_editing_name_required(self):
        self.degree_template_page.click_edit_unit_reqt(template.unit_reqts[1])
        self.degree_template_page.enter_unit_reqt_name('')
        assert not self.degree_template_page.is_unit_reqt_save_enabled()

    def test_unit_reqt_editing_name_max_255_chars(self):
        name = template.unit_reqts[1].name * 20
        self.degree_template_page.enter_unit_reqt_name(name)
        utils.assert_equivalence(self.degree_template_page.unit_reqt_name_input_value(), name[0:255])

    def test_unit_reqt_editing_unit_count_required(self):
        self.degree_template_page.enter_unit_reqt_num('')
        assert not self.degree_template_page.is_unit_reqt_save_enabled()

    def test_unit_reqt_editing_cancel(self):
        self.degree_template_page.click_cancel_unit_reqt()

    def test_unit_reqt_editing_saved(self):
        reqt = template.unit_reqts[1]
        reqt.name = f'EDITED {reqt.name}'
        reqt.unit_count = f'{int(reqt.unit_count) - 1}'
        self.degree_template_page.edit_unit_reqt(reqt)
        utils.assert_equivalence(self.degree_template_page.visible_unit_reqt_name(reqt), reqt.name)
        utils.assert_equivalence(self.degree_template_page.visible_unit_reqt_num(reqt), reqt.unit_count)

    def test_unit_reqt_deletion_cancel(self):
        self.degree_template_page.click_delete_unit_reqt(template.unit_reqts[0])
        self.degree_template_page.click_cancel_delete()

    def test_unit_reqt_deletion(self):
        reqt = template.unit_reqts[0]
        self.degree_template_page.click_delete_unit_reqt(reqt)
        self.degree_template_page.click_confirm_delete()
        self.degree_template_page.when_not_present(self.degree_template_page.unit_reqt_name_loc(reqt),
                                                   utils.get_short_timeout())


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtCategoryCreation:

    def test_category_type_required(self):
        self.degree_template_page.click_add_col_reqt_button(1)
        self.degree_template_page.when_present(self.degree_template_page.COL_REQT_CREATE_BUTTON, 1)
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_no_sub_category_or_course_if_no_category(self):
        opt_els = self.degree_template_page.col_reqt_type_options()
        sub_cat_opt = next(filter(lambda o: o.text == 'Subcategory', opt_els))
        course_opt = next(filter(lambda o: o.text == 'Course Requirement', opt_els))
        assert not sub_cat_opt.is_enabled()
        assert not course_opt.is_enabled()

    def test_category_creation_name_required(self):
        self.degree_template_page.select_col_reqt_type('Category')
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_category_creation_name_max_255_chars(self):
        name = cat_1.name * 20
        self.degree_template_page.enter_col_reqt_name(name)
        utils.assert_equivalence(self.degree_template_page.col_reqt_name_input_value(), name[0:255])

    def test_category_creation_desc_not_required(self):
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_category_creation_cancel(self):
        self.degree_template_page.click_cancel_col_reqt()

    def test_category_creation_saved(self):
        self.degree_template_page.create_col_reqt(cat_1, template)

    def test_category_creation_name_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_cat_name(cat_1), cat_1.name)

    def test_category_creation_desc_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_cat_desc(cat_1), cat_1.desc)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtSubCategoryCreation:

    def test_sub_category_creation_name_required(self):
        self.degree_template_page.click_add_col_reqt_button(1)
        self.degree_template_page.select_col_reqt_type('Subcategory')
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_category_creation_name_max_255_chars(self):
        name = sub_cat_1.name * 20
        self.degree_template_page.enter_col_reqt_name(name)
        utils.assert_equivalence(self.degree_template_page.col_reqt_name_input_value(), name[0:255])

    def test_sub_category_creation_parent_category_required(self):
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_category_creation_parent_category_selection(self):
        self.degree_template_page.select_col_reqt_parent(cat_1)

    def test_sub_category_creation_desc_not_required(self):
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_category_creation_cancel(self):
        self.degree_template_page.click_cancel_col_reqt()

    def test_sub_category_creation_saved(self):
        self.degree_template_page.create_col_reqt(sub_cat_1, template)

    def test_sub_category_creation_name_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_cat_name(sub_cat_1), sub_cat_1.name)

    def test_sub_category_creation_desc_saved_with_link(self):
        link_loc = By.XPATH, '//a[contains(@href, "Teena_Marie")]'
        assert self.degree_template_page.is_external_link_valid(link_loc, 'Teena Marie - Wikipedia')

    def test_sub_category_creation_no_sub_categories_as_parents(self):
        self.degree_template_page.click_add_col_reqt_button(1)
        self.degree_template_page.select_col_reqt_type('Subcategory')
        opt = next(filter(lambda el: el.text == sub_cat_1.name, self.degree_template_page.col_reqt_parent_options()))
        assert not opt.is_enabled()


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtSubCategoryCourseCreation:

    def test_sub_cat_course_creation_name_required(self):
        self.degree_template_page.click_cancel_col_reqt()
        self.degree_template_page.click_add_col_reqt_button(1)
        self.degree_template_page.select_col_reqt_type('Course Requirement')
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_course_creation_name_max_255_chars(self):
        name = sub_cat_1_course_1.name * 20
        self.degree_template_page.enter_col_reqt_name(name)
        utils.assert_equivalence(self.degree_template_page.col_reqt_name_input_value(), name[0:255])

    def test_sub_cat_course_creation_parent_required(self):
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_course_creation_parent_selection(self):
        self.degree_template_page.select_col_reqt_parent(sub_cat_1)

    def test_sub_cat_course_creation_no_description(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.COL_REQT_DESC_INPUT)

    def test_sub_cat_course_creation_units_not_required(self):
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_course_creation_units_must_be_numeric(self):
        self.degree_template_page.enter_col_reqt_units('4A')
        self.degree_template_page.wait_for_units_numeric_error_msg()

    def test_sub_cat_course_creation_units_max_4_chars(self):
        self.degree_template_page.enter_col_reqt_units('3.351')
        utils.assert_equivalence(self.degree_template_page.col_reqt_unit_input_0_value(), '3.35')

    def test_sub_cat_course_creation_units_range_allowed(self):
        self.degree_template_page.enter_col_reqt_units('4-5')

    def test_sub_cat_course_creation_unit_reqt_fulfillment_not_required(self):
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_course_creation_unit_reqt_fulfillment_selection(self):
        reqt = template.categories[0].sub_categories[0].course_reqts[0].unit_reqts[0]
        self.degree_template_page.select_col_reqt_unit_reqt(reqt)
        self.degree_template_page.when_present(
            self.degree_template_page.col_reqt_unit_reqt_remove_button(reqt), 1)

    def test_sub_cat_course_creation_cancel(self):
        self.degree_template_page.click_cancel_col_reqt()

    def test_sub_cat_course_creation_saved(self):
        self.degree_template_page.create_col_reqt(sub_cat_1_course_1, template)

    def test_sub_cat_course_creation_name_saved(self):
        actual = self.degree_template_page.visible_template_course_reqt_name(sub_cat_1_course_1)
        utils.assert_equivalence(actual, sub_cat_1_course_1.name)

    def test_sub_cat_course_creation_units_saved(self):
        actual = self.degree_template_page.visible_template_course_reqt_units(sub_cat_1_course_1)
        utils.assert_equivalence(actual, sub_cat_1_course_1.units)

    def test_sub_cat_course_creation_unit_reqts_saved(self):
        actual = self.degree_template_page.visible_template_course_reqt_fulfillment(sub_cat_1_course_1)
        utils.assert_actual_includes_expected(actual, sub_cat_1_course_1.unit_reqts[0].name)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtSubCategoryCourseEditing:

    def test_sub_cat_course_editing_name_required(self):
        self.degree_template_page.click_edit_cat(sub_cat_1_course_1)
        self.degree_template_page.enter_col_reqt_name('')
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_course_editing_parent_required(self):
        self.degree_template_page.enter_col_reqt_name(sub_cat_1_course_1.name)
        self.degree_template_page.select_col_reqt_parent()
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_course_editing_no_description(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.COL_REQT_DESC_INPUT)

    def test_sub_cat_course_editing_units_not_required(self):
        self.degree_template_page.select_col_reqt_parent(sub_cat_1)
        self.degree_template_page.enter_col_reqt_units('')
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_course_editing_unit_reqt_fulfillment_not_required(self):
        self.degree_template_page.remove_col_reqt_unit_reqt(sub_cat_1_course_1.unit_reqts[0])
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_course_editing_cancel(self):
        self.degree_template_page.click_cancel_col_reqt()

    def test_sub_cat_course_editing_saved(self):
        sub_cat_1_course_1.name = f'EDITED {sub_cat_1_course_1.name}'
        sub_cat_1_course_1.parent = sub_cat_1
        sub_cat_1_course_1.units = ''
        sub_cat_1_course_1.unit_reqts = [template.unit_reqts[2]]
        self.degree_template_page.click_edit_cat(sub_cat_1_course_1)
        self.degree_template_page.enter_col_reqt_metadata(sub_cat_1_course_1)
        self.degree_template_page.save_col_reqt()
        self.degree_template_page.when_present(self.degree_template_page.course_reqt_row(sub_cat_1_course_1),
                                               utils.get_short_timeout())

    def test_sub_cat_course_editing_name_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_template_course_reqt_name(sub_cat_1_course_1),
                                 sub_cat_1_course_1.name)

    def test_sub_cat_course_editing_units_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_template_course_reqt_units(sub_cat_1_course_1),
                                 '—')

    def test_sub_cat_course_editing_unit_reqts_saved(self):
        utils.assert_actual_includes_expected(
            self.degree_template_page.visible_template_course_reqt_fulfillment(sub_cat_1_course_1),
            sub_cat_1_course_1.unit_reqts[0].name)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtSubCategoryCourseDeletion:

    def test_sub_cat_course_deletion_cancel(self):
        self.degree_template_page.click_delete_cat(sub_cat_1_course_1)
        self.degree_template_page.click_cancel_delete()

    def test_sub_cat_course_deletion(self):
        self.degree_template_page.click_delete_cat(sub_cat_1_course_1)
        self.degree_template_page.click_confirm_delete()
        self.degree_template_page.when_not_present(self.degree_template_page.course_reqt_row(sub_cat_1_course_1), 2)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtSubCategoryEditing:

    def test_sub_cat_editing_setup(self):
        self.degree_template_page.create_col_reqt(cat_2, template)
        self.degree_template_page.create_col_reqt(sub_cat_1_course_2, template)

    def test_sub_cat_editing_name_required(self):
        self.degree_template_page.click_edit_cat(sub_cat_1)
        self.degree_template_page.enter_col_reqt_name('')
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_editing_parent_required(self):
        self.degree_template_page.enter_col_reqt_name(sub_cat_1.name)
        self.degree_template_page.select_col_reqt_parent()
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_editing_description_not_required(self):
        self.degree_template_page.select_col_reqt_parent(cat_1)
        self.degree_template_page.enter_col_reqt_desc('')
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_sub_cat_editing_cancel(self):
        self.degree_template_page.click_cancel_col_reqt()

    def test_sub_cat_editing_saved(self):
        sub_cat_1.name = f'EDITED {sub_cat_1.name}'
        sub_cat_1.parent = cat_2
        self.degree_template_page.click_edit_cat(sub_cat_1)
        self.degree_template_page.enter_col_reqt_metadata(sub_cat_1)
        self.degree_template_page.save_col_reqt()

    def test_sub_cat_editing_name_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_cat_name(sub_cat_1), sub_cat_1.name)

    def test_sub_cat_editing_desc_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_cat_desc(sub_cat_1), sub_cat_1.desc)

    def test_sub_cat_editing_sub_cat_courses_updated(self):
        utils.assert_equivalence(self.degree_template_page.visible_template_course_reqt_name(sub_cat_1_course_2),
                                 sub_cat_1_course_2.name)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtSubCategoryDeletion:

    def test_sub_cat_deletion_cancel(self):
        self.degree_template_page.click_delete_cat(sub_cat_1)
        self.degree_template_page.click_cancel_delete()

    def test_sub_cat_deletion(self):
        self.degree_template_page.click_delete_cat(sub_cat_1)
        self.degree_template_page.click_confirm_delete()
        self.degree_template_page.when_not_present(self.degree_template_page.cat_name_loc(sub_cat_1), 2)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtCategoryCourseCreation:

    def test_cat_course_creation_name_required(self):
        self.degree_template_page.click_add_col_reqt_button(1)
        self.degree_template_page.select_col_reqt_type('Course Requirement')
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_course_creation_name_max_255_chars(self):
        name = cat_1_course_1.name * 20
        self.degree_template_page.enter_col_reqt_name(name)
        utils.assert_equivalence(self.degree_template_page.col_reqt_name_input_value(), name[0:255])

    def test_cat_course_creation_parent_required(self):
        assert not self.degree_template_page.is_col_reqt_create_enabled()
        self.degree_template_page.select_col_reqt_parent(cat_1)

    def test_cat_course_creation_no_desc(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.COL_REQT_DESC_INPUT)

    def test_cat_course_creation_units_not_required(self):
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_course_creation_units_must_be_numeric(self):
        self.degree_template_page.enter_col_reqt_units('4A')
        self.degree_template_page.wait_for_units_numeric_error_msg()

    def test_cat_course_creation_units_max_4_chars(self):
        self.degree_template_page.enter_col_reqt_units('3.351')
        utils.assert_equivalence(self.degree_template_page.col_reqt_unit_input_0_value(), '3.35')

    def test_cat_course_creation_units_range_allowed(self):
        self.degree_template_page.enter_col_reqt_units('4-5')

    def test_cat_course_creation_unit_reqt_fulfillment_not_required(self):
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_course_creation_unit_reqt_fulfillment_selection(self):
        self.degree_template_page.select_col_reqt_unit_reqt(cat_1_course_1.unit_reqts[0])
        self.degree_template_page.when_present(
            self.degree_template_page.col_reqt_unit_reqt_remove_button(cat_1_course_1.unit_reqts[0]),
            utils.get_short_timeout())

    def test_cat_course_creation_cancel(self):
        self.degree_template_page.click_cancel_col_reqt()

    def test_cat_course_creation_saved(self):
        self.degree_template_page.create_col_reqt(cat_1_course_1, template)

    def test_cat_course_creation_name_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_template_course_reqt_name(cat_1_course_1),
                                 cat_1_course_1.name)

    def test_cat_course_creation_units_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_template_course_reqt_units(cat_1_course_1),
                                 cat_1_course_1.units)

    def test_cat_course_creation_unit_reqts_saved(self):
        utils.assert_actual_includes_expected(
            self.degree_template_page.visible_template_course_reqt_fulfillment(cat_1_course_1),
            cat_1_course_1.unit_reqts[0].name)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtCategoryCourseEditing:

    def test_cat_course_editing_setup(self):
        self.degree_template_page.create_col_reqt(sub_cat_2, template)

    def test_cat_course_editing_name_required(self):
        self.degree_template_page.click_edit_cat(cat_1_course_1)
        self.degree_template_page.enter_col_reqt_name('')
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_course_editing_parent_required(self):
        self.degree_template_page.enter_col_reqt_name(cat_1_course_1.name)
        self.degree_template_page.select_col_reqt_parent()
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_course_editing_no_description(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.COL_REQT_DESC_INPUT)

    def test_cat_course_editing_units_not_required(self):
        self.degree_template_page.select_col_reqt_parent(cat_1)
        self.degree_template_page.enter_col_reqt_units('')
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_course_editing_unit_reqt_fulfillment_not_required(self):
        self.degree_template_page.remove_col_reqt_unit_reqt(cat_1_course_1.unit_reqts[0])
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_course_editing_cancel(self):
        self.degree_template_page.click_cancel_col_reqt()

    def test_cat_course_editing_saved(self):
        cat_1_course_1.name = f'EDITED {cat_1_course_1.name}'
        cat_1_course_1.parent = sub_cat_2
        self.degree_template_page.units = '10'
        self.degree_template_page.unit_reqts = [template.unit_reqts[2]]
        self.degree_template_page.click_edit_cat(cat_1_course_1)
        self.degree_template_page.enter_col_reqt_metadata(cat_1_course_1)
        self.degree_template_page.save_col_reqt()

    def test_cat_course_editing_name_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_template_course_reqt_name(cat_1_course_1),
                                 cat_1_course_1.name)

    def test_cat_course_editing_units_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_template_course_reqt_units(cat_1_course_1),
                                 cat_1_course_1.units)

    def test_cat_course_editing_unit_reqts_saved(self):
        utils.assert_actual_includes_expected(
            self.degree_template_page.visible_template_course_reqt_fulfillment(cat_1_course_1),
            cat_1_course_1.unit_reqts[0].name)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtCategoryCourseDeletion:

    def test_cat_course_deletion_cancel(self):
        self.degree_template_page.click_delete_cat(cat_1_course_1)
        self.degree_template_page.click_cancel_delete()

    def test_cat_course_deletion(self):
        self.degree_template_page.click_delete_cat(cat_1_course_1)
        self.degree_template_page.click_confirm_delete()
        self.degree_template_page.when_not_present(self.degree_template_page.course_reqt_row(cat_1_course_1), 2)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtCategoryEditing:

    def test_cat_editing_name_required(self):
        self.degree_template_page.click_edit_cat(cat_1)
        self.degree_template_page.enter_col_reqt_name('')
        assert not self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_editing_description_not_required(self):
        self.degree_template_page.enter_col_reqt_name(cat_1.name)
        self.degree_template_page.enter_col_reqt_desc('')
        assert self.degree_template_page.is_col_reqt_create_enabled()

    def test_cat_editing_cancel(self):
        self.degree_template_page.click_cancel_col_reqt()

    def test_cat_editing_saved(self):
        cat_1.name = f'EDITED {cat_1.name}'
        cat_1.desc = f'EDITED {cat_1.desc}'
        self.degree_template_page.click_edit_cat(cat_1)
        self.degree_template_page.enter_col_reqt_metadata(cat_1)
        self.degree_template_page.save_col_reqt()

    def test_cat_editing_name_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_cat_name(cat_1), cat_1.name)

    def test_cat_editing_desc_saved(self):
        utils.assert_equivalence(self.degree_template_page.visible_cat_desc(cat_1), cat_1.desc)


@pytest.mark.usefixtures('page_objects')
class TestColumnReqtCategoryDeletion:

    def test_cat_deletion_cancel(self):
        self.degree_template_page.click_delete_cat(cat_1)
        self.degree_template_page.click_cancel_delete()

    def test_cat_deletion(self):
        self.degree_template_page.click_delete_cat(cat_1)
        self.degree_template_page.click_confirm_delete()
        self.degree_template_page.when_not_present(self.degree_template_page.cat_name_loc(cat_1), 2)


@pytest.mark.usefixtures('page_objects')
class TestCampusReqts:
    default_desc = 'American History, American Institutions, and American Cultures courses can also count as H/SS courses.'

    def test_select_reqts(self):
        self.degree_template_page.click_add_col_reqt_button(3)
        self.degree_template_page.select_col_reqt_type('Campus Requirements')

    def test_default_description(self):
        self.degree_template_page.when_present(self.degree_template_page.COL_REQT_DESC_INPUT, 2)
        utils.assert_equivalence(self.degree_template_page.col_reqt_desc_input_value(), self.default_desc)

    def test_no_name_input(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.COL_REQT_NAME_INPUT)

    def test_no_units_input(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.COL_REQT_COURSE_UNITS_INPUT)

    def test_no_units_reqt_selection(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.COL_REQT_COURSE_UNITS_REQT_SELECT)

    def test_no_parent_selection(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.COL_REQT_PARENT_SELECT)

    def test_save_campus_reqts(self):
        self.degree_template_page.save_col_reqt()
        self.degree_template_page.when_present(self.degree_template_page.campus_reqt_row('Entry Level Writing'),
                                               utils.get_short_timeout())
        assert self.degree_template_page.is_present(self.degree_template_page.campus_reqt_row('American History'))
        assert self.degree_template_page.is_present(self.degree_template_page.campus_reqt_row('American Institutions'))
        assert self.degree_template_page.is_present(self.degree_template_page.campus_reqt_row('American Cultures'))

    def test_no_adding_twice(self):
        self.degree_template_page.click_add_col_reqt_button(1)
        opt_els = self.degree_template_page.col_reqt_type_options()
        reqts_opt = next(filter(lambda o: o.text == 'Campus Requirements', opt_els))
        assert not reqts_opt.is_enabled()

    def test_visible_description(self):
        self.degree_template_page.click_cancel_col_reqt()
        utils.assert_equivalence(self.degree_template_page.campus_reqts_desc(3), self.default_desc)

    def test_edit_description(self):
        new_desc = f'EDITED {self.default_desc}'
        self.degree_template_page.edit_campus_reqts_desc(3, new_desc)
        utils.assert_equivalence(self.degree_template_page.campus_reqts_desc(3), new_desc)

    def test_delete_reqts(self):
        self.degree_template_page.delete_campus_reqts(3)
        self.degree_template_page.when_not_present(self.degree_template_page.campus_reqt_row('Entry Level Writing'),
                                                   utils.get_short_timeout())
        assert not self.degree_template_page.is_present(self.degree_template_page.campus_reqt_row('American History'))
        assert not self.degree_template_page.is_present(
            self.degree_template_page.campus_reqt_row('American Institutions'))
        assert not self.degree_template_page.is_present(self.degree_template_page.campus_reqt_row('American Cultures'))


@pytest.mark.usefixtures('page_objects')
class TestTemplateRenaming:

    def test_new_name_required(self):
        self.degree_template_page.click_degree_checks()
        self.degree_template_mgmt_page.click_rename_button(template)
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.RENAME_DEGREE_SAVE_BUTTON,
                                                    utils.get_short_timeout())
        utils.assert_equivalence(self.degree_template_mgmt_page.new_name_input_value(), template.name)
        assert self.degree_template_mgmt_page.element(
            self.degree_template_mgmt_page.RENAME_DEGREE_SAVE_BUTTON).is_enabled()

    def test_new_name_saved(self):
        name = f'{template.name} - Edited'
        self.degree_template_mgmt_page.enter_new_name(name)
        self.degree_template_mgmt_page.click_save_new_name()
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.degree_check_link(template),
                                                    utils.get_short_timeout())
        template.name = name

    def test_new_name_cancel(self):
        self.degree_template_mgmt_page.click_rename_button(template)
        self.degree_template_mgmt_page.click_cancel_new_name()
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.degree_check_link(template),
                                                    utils.get_short_timeout())


@pytest.mark.usefixtures('page_objects')
class TestTemplateCopying:
    template_copy = DegreeCheckTemplate({'name': f'Teena Template COPY {test.test_id}'})

    def test_unique_name_required(self):
        self.degree_template_mgmt_page.click_copy_button(template)
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.COPY_DEGREE_SAVE_BUTTON,
                                                    utils.get_short_timeout())
        utils.assert_equivalence(self.degree_template_mgmt_page.copy_name_input_value(), template.name)
        assert not self.degree_template_mgmt_page.element(
            self.degree_template_mgmt_page.COPY_DEGREE_SAVE_BUTTON).is_enabled()

    def test_max_255_chars(self):
        name = template.name * 20
        self.degree_template_mgmt_page.enter_copy_name(name)
        utils.assert_equivalence(self.degree_template_mgmt_page.copy_name_input_value(), name[0:255])

    def test_cancel_copy(self):
        self.degree_template_mgmt_page.click_cancel_copy()
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.degree_check_link(template),
                                                    utils.get_short_timeout())

    def test_save_copy(self):
        self.degree_template_mgmt_page.click_copy_button(template)
        self.degree_template_mgmt_page.enter_copy_name(self.template_copy.name)
        self.degree_template_mgmt_page.click_save_copy()
        self.degree_template_mgmt_page.when_present(
            self.degree_template_mgmt_page.degree_check_link(self.template_copy),
            utils.get_short_timeout())


@pytest.mark.usefixtures('page_objects')
class TestTemplateDeletion:

    def test_deletion_cancel(self):
        self.degree_template_mgmt_page.click_delete_degree(template)
        self.degree_template_mgmt_page.click_cancel_delete()

    def test_deletion_save(self):
        self.degree_template_mgmt_page.click_delete_degree(template)
        self.degree_template_mgmt_page.click_confirm_delete()
        self.degree_template_mgmt_page.when_not_present(self.degree_template_mgmt_page.degree_check_link(template),
                                                        utils.get_short_timeout())
