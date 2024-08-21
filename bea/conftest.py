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

import os

from bea.models.term import Term
from bea.pages.admit_page import AdmitPage
from bea.pages.api_admin_page import ApiAdminPage
from bea.pages.api_notes_page import ApiNotesPage
from bea.pages.calnet_page import CalNetPage
from bea.pages.class_page import ClassPage
from bea.pages.curated_students_page import CuratedStudentsPage
from bea.pages.filtered_admits_page import FilteredAdmitsPage
from bea.pages.filtered_students_page import FilteredStudentsPage
from bea.pages.flight_deck_page import FlightDeckPage
from bea.pages.homepage import Homepage
from bea.pages.search_form import SearchForm
from bea.pages.search_results_page import SearchResultsPage
from bea.pages.student_page import StudentPage
from bea.test_utils.webdriver_manager import WebDriverManager
from boac.factory import create_app
import pytest


os.environ['BOAC_ENV'] = 'bea'  # noqa

_app = create_app()

ctx = _app.app_context()
ctx.push()


def pytest_addoption(parser):
    parser.addoption('--browser', action='store', default=_app.config['BROWSER'])
    parser.addoption('--headless', action='store')


@pytest.fixture(scope='session')
def page_objects(request):
    browser = request.config.getoption('--browser')
    headless = request.config.getoption('--headless')
    driver = WebDriverManager.launch_browser(browser=browser, headless=headless)

    term = Term

    # Define page objects

    admit_page = AdmitPage(driver, headless)
    api_admin_page = ApiAdminPage(driver, headless)
    api_notes_page = ApiNotesPage(driver, headless)
    calnet_page = CalNetPage(driver, headless)
    class_page = ClassPage(driver, headless)
    curated_students_page = CuratedStudentsPage(driver, headless)
    filtered_admits_page = FilteredAdmitsPage(driver, headless)
    filtered_students_page = FilteredStudentsPage(driver, headless)
    flight_deck_page = FlightDeckPage(driver, headless)
    homepage = Homepage(driver, headless)
    search_form = SearchForm(driver, headless)
    search_results_page = SearchResultsPage(driver, headless)
    student_page = StudentPage(driver, headless)

    session = request.node
    try:
        for item in session.items:
            cls = item.getparent(pytest.Class)
            setattr(cls.obj, 'driver', driver)
            setattr(cls.obj, 'term', term)
            setattr(cls.obj, 'admit_page', admit_page)
            setattr(cls.obj, 'api_admin_page', api_admin_page)
            setattr(cls.obj, 'api_notes_page', api_notes_page)
            setattr(cls.obj, 'calnet_page', calnet_page)
            setattr(cls.obj, 'class_page', class_page)
            setattr(cls.obj, 'curated_students_page', curated_students_page)
            setattr(cls.obj, 'filtered_admits_page', filtered_admits_page)
            setattr(cls.obj, 'filtered_students_page', filtered_students_page)
            setattr(cls.obj, 'flight_deck_page', flight_deck_page)
            setattr(cls.obj, 'homepage', homepage)
            setattr(cls.obj, 'search_form', search_form)
            setattr(cls.obj, 'search_results_page', search_results_page)
            setattr(cls.obj, 'student_page', student_page)
        yield
    finally:
        WebDriverManager.quit_browser(driver)
