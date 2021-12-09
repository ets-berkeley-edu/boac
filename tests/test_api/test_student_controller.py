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

from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
import pytest
import simplejson as json
from tests.util import override_config

admin_uid = '2040'
asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'
coe_scheduler_uid = '6972201'


@pytest.fixture()
def admin_login(fake_auth):
    fake_auth.login(admin_uid)


@pytest.fixture()
def asc_advisor_login(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor_login(fake_auth):
    fake_auth.login(coe_advisor_uid)


@pytest.fixture()
def coe_scheduler_login(fake_auth):
    fake_auth.login(coe_scheduler_uid)


@pytest.fixture()
def no_canvas_data_access_advisor_login(fake_auth):
    fake_auth.login('1')


@pytest.mark.usefixtures('db_session')
class TestStudent:
    """Student API."""

    @classmethod
    def _api_student_by_sid(cls, client, sid, expected_status_code=200):
        response = client.get(f'/api/student/by_sid/{sid}')
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_student_by_uid(cls, client, uid, expected_status_code=200):
        response = client.get(f'/api/student/by_uid/{uid}')
        assert response.status_code == expected_status_code
        return response.json

    asc_student = {
        'sid': '2345678901',
        'uid': '98765',
    }
    coe_student = {
        'sid': '7890123456',
        'uid': '1049291',
    }
    asc_student_in_coe = {
        'sid': '11667051',
        'uid': '61889',
    }
    unrecognized_student = {
        'sid': '9999999',
        'uid': '9999999',
    }

    @pytest.fixture()
    def admin_auth(self, fake_auth):
        fake_auth.login('2040')

    @staticmethod
    def get_course_for_code(student, term_id, code):
        term = next((term for term in student['enrollmentTerms'] if term['termId'] == term_id), None)
        if term:
            return next((course for course in term['enrollments'] if course['displayName'] == code), None)

    def test_user_feed_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._api_student_by_sid(client=client, sid=self.asc_student['sid'], expected_status_code=401)
        self._api_student_by_uid(client=client, uid=self.asc_student['uid'], expected_status_code=401)

    def test_deny_scheduler(self, client, coe_scheduler_login):
        """Returns 401 if user is scheduler."""
        self._api_student_by_sid(client=client, sid=self.asc_student['sid'], expected_status_code=401)

    def test_user_with_no_enrollments_in_current_term(self, asc_advisor_login, client):
        """Flags student with no enrollments in current term and appends the current term."""
        sid = self.asc_student['sid']
        uid = self.asc_student['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            enrollment_terms = student['enrollmentTerms']
            assert len(enrollment_terms) == 3
            assert [t['termName'] for t in enrollment_terms] == ['Summer 2017', 'Spring 2017', 'Fall 2017']

    def test_user_feed_authenticated(self, client, coe_advisor_login):
        """Returns a well-formed response if authenticated."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            assert student['sid'] == sid
            assert student['uid'] == uid
            assert student['canvasUserId'] == '9000100'

            assert len(student['enrollmentTerms']) > 0
            for term in student['enrollmentTerms']:
                assert len(term['enrollments']) > 0
                for course in term['enrollments']:
                    for canvas_site in course['canvasSites']:
                        assert canvas_site['canvasCourseId']
                        assert canvas_site['courseCode']
                        assert canvas_site['courseTerm']
                        assert canvas_site['courseCode']
                        assert canvas_site['analytics']

    def test_user_feed_holds(self, asc_advisor_login, client):
        """Returns holds if any."""
        response = client.get('/api/student/by_uid/9933311')
        assert response.status_code == 200
        holds = response.json['notifications']['hold']
        assert len(holds) == 2
        assert holds[0]['reason']['description'] == 'Past due balance'
        assert holds[0]['reason']['formalDescription'].startswith('Your student account has a past due balance')
        assert holds[1]['reason']['description'] == 'Semester Out'
        assert holds[1]['reason']['formalDescription'].startswith('You are not eligible to register')

    def test_user_feed_multiple_terms(self, client, coe_advisor_login):
        """Returns all terms with enrollment data in reverse order."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            assert len(student['enrollmentTerms']) == 4
            assert student['enrollmentTerms'][0]['termName'] == 'Spring 2018'
            assert student['enrollmentTerms'][0]['academicYear'] == '2018'
            assert student['enrollmentTerms'][0]['enrolledUnits'] == 3
            assert student['enrollmentTerms'][0]['termGpa']['gpa'] == 2.9
            assert student['enrollmentTerms'][0]['academicStanding']['status'] == 'GST'
            assert len(student['enrollmentTerms'][0]['enrollments']) == 1
            assert student['enrollmentTerms'][1]['termName'] == 'Fall 2017'
            assert student['enrollmentTerms'][1]['academicYear'] == '2018'
            assert student['enrollmentTerms'][1]['enrolledUnits'] == 12.5
            assert student['enrollmentTerms'][1]['termGpa']['gpa'] == 1.8
            assert student['enrollmentTerms'][1]['academicStanding']['status'] == 'PRO'
            assert len(student['enrollmentTerms'][1]['enrollments']) == 5
            assert student['enrollmentTerms'][2]['termName'] == 'Spring 2017'
            assert student['enrollmentTerms'][2]['academicYear'] == '2017'
            assert student['enrollmentTerms'][2]['enrolledUnits'] == 10
            assert student['enrollmentTerms'][2]['termGpa']['gpa'] == 2.7
            assert len(student['enrollmentTerms'][2]['enrollments']) == 3
            assert student['enrollmentTerms'][2]['academicStanding']['status'] == 'GST'
            assert student['enrollmentTerms'][3]['termName'] == 'Spring 2016'
            assert student['enrollmentTerms'][3]['academicYear'] == '2016'
            assert student['enrollmentTerms'][3]['enrolledUnits'] == 0
            assert student['enrollmentTerms'][3]['termGpa']['gpa'] == 3.8
            assert student['enrollmentTerms'][3]['academicStanding']['status'] == 'GST'
            assert len(student['enrollmentTerms'][3]['enrollments']) == 1

    def test_user_feed_academic_standing(self, client, coe_advisor_login):
        """Includes standalone academic standing feed, in addition to per-term merges."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            assert len(student['academicStanding']) == 5
            assert student['academicStanding'][0] == {
                'actionDate': '2018-05-31',
                'sid': '11667051',
                'status': 'GST',
                'termId': '2182',
                'termName': 'Spring 2018',
            }
            assert student['academicStanding'][1] == {
                'actionDate': '2017-12-30',
                'termId': '2178',
                'termName': 'Fall 2017',
                'sid': '11667051',
                'status': 'PRO',
            }

    def test_user_feed_earliest_term_cutoff(self, client, coe_advisor_login):
        """Ignores terms before the configured earliest term."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            for term in student['enrollmentTerms']:
                assert term['termName'] != 'Spring 2001'

    def test_user_feed_future_term_cutoff(self, client, coe_advisor_login):
        """Ignores terms after the configured future term."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            for term in student['enrollmentTerms']:
                assert term['termName'] != 'Summer 2018'

    def test_enrollment_without_course_site(self, client, coe_advisor_login):
        """Returns enrollments with no associated course sites."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            enrollment_without_site = self.get_course_for_code(student, '2172', 'MUSIC 41C')
            assert enrollment_without_site['title'] == 'Private Carillon Lessons for Advanced Students'
            assert enrollment_without_site['canvasSites'] == []

    def test_enrollment_with_multiple_course_sites(self, client, coe_advisor_login):
        """Returns multiple course sites associated with an enrollment, sorted by site id."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            enrollment_with_multiple_sites = self.get_course_for_code(student, '2178', 'NUC ENG 124')
            canvas_sites = enrollment_with_multiple_sites['canvasSites']
            assert len(canvas_sites) == 2
            assert canvas_sites[0]['courseName'] == 'Radioactive Waste Management'
            assert canvas_sites[1]['courseName'] == 'Optional Friday Night Radioactivity Group'

    def test_multiple_primary_section_enrollments(self, client, coe_advisor_login):
        """Disambiguates multiple primary sections under a single course display name."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            classics_first = self.get_course_for_code(student, '2172', 'CLASSIC 130 LEC 001')
            classics_second = self.get_course_for_code(student, '2172', 'CLASSIC 130 LEC 002')
            assert len(classics_first['sections']) == 1
            assert classics_first['sections'][0]['units'] == 4
            assert classics_first['sections'][0]['gradingBasis'] == 'P/NP'
            assert classics_first['sections'][0]['grade'] == 'P'
            assert classics_first['units'] == 4
            assert classics_first['gradingBasis'] == 'P/NP'
            assert classics_first['grade'] == 'P'

            assert len(classics_second['sections']) == 1
            assert classics_second['sections'][0]['units'] == 4
            assert classics_second['sections'][0]['gradingBasis'] == 'Letter'
            assert classics_second['sections'][0]['grade'] == 'B-'
            assert classics_second['units'] == 4
            assert classics_second['gradingBasis'] == 'Letter'
            assert classics_second['grade'] == 'B-'

    def test_enrollments_sorted(self, client, coe_advisor_login):
        """Sorts enrollments by course display name."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            spring_2017_enrollments = student['enrollmentTerms'][2]['enrollments']
            assert(spring_2017_enrollments[0]['displayName'] == 'CLASSIC 130 LEC 001')
            assert(spring_2017_enrollments[1]['displayName'] == 'CLASSIC 130 LEC 002')
            assert(spring_2017_enrollments[2]['displayName'] == 'MUSIC 41C')

    def test_course_site_without_enrollment(self, client, coe_advisor_login):
        """Returns course sites with no associated enrollments."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            assert len(student['enrollmentTerms'][0]['unmatchedCanvasSites']) == 0
            assert len(student['enrollmentTerms'][1]['unmatchedCanvasSites']) == 0
            assert len(student['enrollmentTerms'][2]['unmatchedCanvasSites']) == 1
            unmatched_site = student['enrollmentTerms'][2]['unmatchedCanvasSites'][0]
            assert unmatched_site['courseCode'] == 'STAT 154'
            assert unmatched_site['courseName'] == 'Modern Statistical Prediction and Machine Learning'
            assert unmatched_site['analytics']

    def test_course_site_without_membership(self, client, coe_advisor_login):
        """Returns a graceful error if the expected membership is not found in the course site."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            course_without_membership = self.get_course_for_code(student, '2178', 'BURMESE 1A')
            for metric in ['assignmentsSubmitted', 'currentScore', 'lastActivity']:
                assert course_without_membership['canvasSites'][0]['analytics'][metric]['error']

    def test_course_site_with_enrollment(self, client, coe_advisor_login):
        """Returns sensible data if the expected enrollment is found in the course site."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            course_with_enrollment = self.get_course_for_code(student, '2178', 'MED ST 205')
            analytics = course_with_enrollment['canvasSites'][0]['analytics']

            assert analytics['assignmentsSubmitted']['student']['raw'] == 8
            assert analytics['assignmentsSubmitted']['student']['percentile'] == 64
            assert analytics['assignmentsSubmitted']['courseDeciles'][0] == 0
            assert analytics['assignmentsSubmitted']['courseDeciles'][9] == 10
            assert analytics['assignmentsSubmitted']['courseDeciles'][10] == 17

            assert analytics['currentScore']['student']['raw'] == 84

            assert analytics['lastActivity']['boxPlottable'] is True
            assert analytics['lastActivity']['student']['raw'] == 1535275620
            assert analytics['lastActivity']['student']['percentile'] == 93
            assert analytics['lastActivity']['displayPercentile'] == '90th'

    def test_suppresses_canvas_data_if_unauthorized(self, client, no_canvas_data_access_advisor_login):
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            course_with_enrollment = self.get_course_for_code(student, '2178', 'MED ST 205')
            assert course_with_enrollment['canvasSites'] == []

    def test_student_not_found(self, coe_advisor_login, client):
        """Returns 404 if no viewable student."""
        sid = self.unrecognized_student['sid']
        uid = self.unrecognized_student['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid, expected_status_code=404)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid, expected_status_code=404)
        for response in [student_by_sid, student_by_uid]:
            assert response['message'] == 'Unknown student'

    def test_sis_enrollment_merge(self, client, coe_advisor_login):
        """Merges sorted SIS enrollment data."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            burmese = self.get_course_for_code(student, '2178', 'BURMESE 1A')
            assert burmese['displayName'] == 'BURMESE 1A'
            assert burmese['title'] == 'Introductory Burmese'
            assert len(burmese['sections']) == 1
            assert burmese['sections'][0]['ccn'] == 90100
            assert burmese['sections'][0]['sectionNumber'] == '001'
            assert burmese['sections'][0]['enrollmentStatus'] == 'E'
            assert burmese['sections'][0]['units'] == 4
            assert burmese['sections'][0]['gradingBasis'] == 'Letter'
            assert burmese['sections'][0]['midtermGrade'] == 'D+'
            assert burmese['sections'][0]['primary'] is True
            assert not burmese['sections'][0]['grade']
            assert burmese['units'] == 4
            assert burmese['gradingBasis'] == 'Letter'
            assert burmese['midtermGrade'] == 'D+'
            assert not burmese['grade']

            medieval = self.get_course_for_code(student, '2178', 'MED ST 205')
            assert medieval['displayName'] == 'MED ST 205'
            assert medieval['title'] == 'Medieval Manuscripts as Primary Sources'
            assert len(medieval['sections']) == 1
            assert medieval['sections'][0]['ccn'] == 90200
            assert medieval['sections'][0]['sectionNumber'] == '001'
            assert medieval['sections'][0]['enrollmentStatus'] == 'E'
            assert medieval['sections'][0]['units'] == 5
            assert medieval['sections'][0]['gradingBasis'] == 'Letter'
            assert medieval['sections'][0]['primary'] is True
            assert not medieval['sections'][0]['grade']

            nuclear = self.get_course_for_code(student, '2178', 'NUC ENG 124')
            assert nuclear['displayName'] == 'NUC ENG 124'
            assert nuclear['title'] == 'Radioactive Waste Management'
            assert len(nuclear['sections']) == 2
            assert nuclear['sections'][0]['ccn'] == 90300
            assert nuclear['sections'][0]['sectionNumber'] == '002'
            assert nuclear['sections'][0]['enrollmentStatus'] == 'E'
            assert nuclear['sections'][0]['units'] == 3
            assert nuclear['sections'][0]['gradingBasis'] == 'P/NP'
            assert nuclear['sections'][0]['grade'] == 'P'
            assert nuclear['sections'][0]['primary'] is True
            assert nuclear['sections'][1]['ccn'] == 90301
            assert nuclear['sections'][1]['sectionNumber'] == '201'
            assert nuclear['sections'][1]['enrollmentStatus'] == 'E'
            assert nuclear['sections'][1]['units'] == 0
            assert nuclear['sections'][1]['gradingBasis'] == 'NON'
            assert nuclear['sections'][1]['primary'] is False
            assert not nuclear['sections'][1]['grade']

            music = self.get_course_for_code(student, '2172', 'MUSIC 41C')
            assert music['displayName'] == 'MUSIC 41C'
            assert music['title'] == 'Private Carillon Lessons for Advanced Students'
            # Represses an obsolete waitlisted section.
            assert len(music['sections']) == 1
            assert music['sections'][0]['ccn'] == 80100
            assert music['sections'][0]['sectionNumber'] == '001'
            assert music['sections'][0]['enrollmentStatus'] == 'E'
            assert music['sections'][0]['units'] == 2
            assert music['sections'][0]['gradingBasis'] == 'Letter'
            assert music['sections'][0]['grade'] == 'A-'
            assert music['sections'][0]['primary'] is True
            assert music['units'] == 2
            assert music['gradingBasis'] == 'Letter'
            assert music['grade'] == 'A-'

    def test_dropped_sections(self, client, coe_advisor_login):
        """Collects dropped sections in a separate feed."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            dropped_sections = student['enrollmentTerms'][1]['droppedSections']
            assert len(dropped_sections) == 1
            assert dropped_sections[0]['displayName'] == 'MUSIC 41C'
            assert dropped_sections[0]['component'] == 'TUT'
            assert dropped_sections[0]['sectionNumber'] == '002'

    def test_generic_haas_advisor(self, client, coe_advisor_login):
        """Populates UCBUGADHAAS advisor with name and email."""
        sid = self.coe_student['sid']
        uid = self.coe_student['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            advisors = student['advisors']
            assert len(advisors) == 2
            assert advisors[0] == {
                'uid': '1',
                'sid': '2',
                'firstName': 'Real',
                'lastName': 'Advisor',
                'email': 'ARealLiveAdvisor@b.e',
                'role': 'College Advisor',
                'title': 'Director of Advising',
                'program': 'Undergrad Business',
                'plan': 'Business Administration BS',
            }
            assert advisors[1] == {
                'uid': None,
                'sid': 'UCBUGADHAAS',
                'firstName': 'Haas Undergraduate Program',
                'lastName': None,
                'email': 'UGMajorAdvising@haas.berkeley.edu',
                'role': 'Major Advisor',
                'title': None,
                'program': 'Undergrad Business',
                'plan': 'Business Administration BS',
            }

    def test_sis_profile(self, client, coe_advisor_login):
        """Provides SIS profile data."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            sis_profile = student['sisProfile']
            assert sis_profile['academicCareer'] == 'UGRD'
            assert sis_profile['cumulativeGPA'] == 3.8
            assert sis_profile['cumulativeUnits'] == 101.3
            assert sis_profile['degreeProgress']['requirements']['americanCultures']['status'] == 'In Progress'
            assert sis_profile['degreeProgress']['requirements']['americanHistory']['status'] == 'Not Satisfied'
            assert sis_profile['degreeProgress']['requirements']['americanInstitutions']['status'] == 'Not Satisfied'
            assert sis_profile['degreeProgress']['requirements']['entryLevelWriting']['status'] == 'Satisfied'
            assert sis_profile['emailAddress'] == 'barnburner@berkeley.edu'
            assert sis_profile['level']['code'] == '30'
            assert sis_profile['level']['description'] == 'Junior'
            assert sis_profile['phoneNumber'] == '415/123-4567'
            assert len(sis_profile['plans']) == 2
            assert sis_profile['plans'][0]['description'] == 'English BA'
            assert sis_profile['plans'][0]['program'] == 'Undergrad Letters & Science'
            assert sis_profile['plans'][0]['degreeProgramUrl'] == 'http://guide.berkeley.edu/undergraduate/degree-programs/english/'
            assert sis_profile['plans'][1]['description'] == 'Nuclear Engineering BS'
            assert sis_profile['plans'][1]['program'] == 'Engineering'
            assert sis_profile['plans'][1]['degreeProgramUrl'] == 'http://guide.berkeley.edu/undergraduate/degree-programs/nuclear-engineering/'
            assert sis_profile['preferredName'] == 'Osk Bear'
            assert sis_profile['primaryName'] == 'Oski Bear'
            assert sis_profile['termsInAttendance'] is None

    def test_sis_profile_expected_graduation_term(self, client, coe_advisor_login):
        """Provides the last of any expected graduation terms listed in SIS profile."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            sis_profile = student['sisProfile']
            assert sis_profile['expectedGraduationTerm']['id'] == '2198'
            assert sis_profile['expectedGraduationTerm']['name'] == 'Fall 2019'

    def test_student_profile_inactive_status(self, client, coe_advisor_login):
        inactive_student_by_sid = self._api_student_by_sid(client=client, sid='3141592653')
        inactive_student_by_uid = self._api_student_by_uid(client=client, uid='314159')
        for student in [inactive_student_by_sid, inactive_student_by_uid]:
            assert student['sid'] == '3141592653'
            assert student['uid'] == '314159'
            assert student['name'] == 'Johannes Climacus'
            assert student['sisProfile']['academicCareer'] == 'UGRD'
            assert student['sisProfile']['academicCareerStatus'] == 'Inactive'
            assert 'SIS-EXTENDED' in student['sisProfile']['calnetAffiliations']
            assert len(student['sisProfile']['plans']) == 3
            assert student['sisProfile']['plans'][0]['description'] == 'Philosophy BA'
            assert student['sisProfile']['plans'][0]['status'] == 'Discontinued'
            assert len(student['enrollmentTerms']) == 2
            assert student['enrollmentTerms'][0]['termName'] == 'Spring 2005'
            assert student['enrollmentTerms'][0]['enrolledUnits'] == 4
            assert len(student['enrollmentTerms'][0]['enrollments']) == 1
            assert student['enrollmentTerms'][0]['enrollments'][0]['displayName'] == 'PHILOS 188'
            assert student['enrollmentTerms'][0]['enrollments'][0]['title'] == 'Phenomenology'
            assert student['enrollmentTerms'][0]['enrollments'][0]['grade'] == 'I'
            assert len(student['enrollmentTerms'][0]['enrollments'][0]['sections']) == 1
            assert student['enrollmentTerms'][0]['enrollments'][0]['sections'][0]['sectionNumber'] == 'X001'
            assert student['enrollmentTerms'][1]['termName'] == 'Fall 2017'
            assert student['enrollmentTerms'][1]['enrolledUnits'] == 0
            assert len(student['enrollmentTerms'][1]['enrollments']) == 0

    def test_student_profile_completed_status(self, client, coe_advisor_login):
        inactive_student_by_sid = self._api_student_by_sid(client=client, sid='2718281828')
        inactive_student_by_uid = self._api_student_by_uid(client=client, uid='271828')
        for student in [inactive_student_by_sid, inactive_student_by_uid]:
            assert student['sid'] == '2718281828'
            assert student['uid'] == '27182'
            assert student['name'] == 'Ernest Pontifex'
            assert student['sisProfile']['academicCareer'] == 'GRAD'
            assert student['sisProfile']['academicCareerStatus'] == 'Completed'
            assert 'FORMER-STUDENT' in student['sisProfile']['calnetAffiliations']

            degree = student['sisProfile']['degrees'][0]
            assert degree['dateAwarded'] == '2010-05-14'
            assert degree['description'] == 'Doctor of Philosophy'
            assert degree['plans'][0]['group'] == 'Graduate Division'
            assert degree['plans'][0]['plan'] == 'English PhD'
            assert len(student['enrollmentTerms']) == 3
            assert student['enrollmentTerms'][0]['termName'] == 'Spring 2010'
            assert student['enrollmentTerms'][1]['termName'] == 'Fall 2005'
            assert student['enrollmentTerms'][1]['enrollments'][0]['title'] == 'Chaucer'

    def test_athletics_profile_non_asc(self, client, coe_advisor_login):
        """Does not include select athletics profile data for non-ASC users."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            assert 'inIntensiveCohort' not in student['athleticsProfile']

    def test_athletics_profile_asc(self, asc_advisor_login, client):
        """Includes athletics profile for ASC users."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            assert student['gender'] == 'Different Identity'
            assert student['underrepresented'] is False

            assert 'coeProfile' not in student
            athletics_profile = student['athleticsProfile']
            assert athletics_profile['inIntensiveCohort'] is True
            assert len(athletics_profile['athletics']) == 2
            hockey = next(a for a in athletics_profile['athletics'] if a['groupCode'] == 'WFH')
            assert hockey['groupName'] == 'Women\'s Field Hockey'
            assert hockey['teamCode'] == 'FHW'
            assert hockey['teamName'] == 'Women\'s Field Hockey'
            tennis = next(a for a in athletics_profile['athletics'] if a['groupCode'] == 'WTE')
            assert tennis['groupName'] == 'Women\'s Tennis'
            assert tennis['teamCode'] == 'TNW'
            assert tennis['teamName'] == 'Women\'s Tennis'

    def test_college_of_engineering_profile(self, client, coe_advisor_login):
        """Includes COE profile (eg, PREP) for COE students."""
        sid = self.coe_student['sid']
        uid = self.coe_student['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            assert student['gender'] == 'Female'
            assert student['underrepresented'] is True

            assert 'inIntensiveCohort' not in student['athleticsProfile']
            assert 'coeProfile' in student
            assert 'degreeChecks' in student

            expected_coe_profile = {
                'didPrep': False,
                'didTprep': False,
                'ethnicity': 'B',
                'gender': 'F',
                'gradTerm': 'sp',
                'gradYear': '2020',
                'inMet': False,
                'isActiveCoe': True,
                'prepEligible': True,
                'probation': False,
                'sat1read': 510,
                'sat2math': 620,
                'sat2read': 520,
                'status': 'C',
                'tprepEligible': False,
                'underrepresented': True,
                'advisorUid': '1133399',
            }
            for key, value in expected_coe_profile.items():
                assert student['coeProfile'].get(key) == value

    def test_athletics_profile_admin(self, admin_login, client):
        """Includes athletics profile for admins."""
        sid = self.asc_student_in_coe['sid']
        uid = self.asc_student_in_coe['uid']
        student_by_sid = self._api_student_by_sid(client=client, sid=sid)
        student_by_uid = self._api_student_by_uid(client=client, uid=uid)
        for student in [student_by_sid, student_by_uid]:
            assert student['gender'] == 'Different Identity'
            assert student['underrepresented'] is False

            athletics_profile = student['athleticsProfile']
            assert athletics_profile['inIntensiveCohort'] is True
            assert len(athletics_profile['athletics']) == 2

    def test_student_with_appointment(self, app, client, asc_advisor_login):
        """Includes advising appointments."""
        student = self._api_student_by_sid(client=client, sid='11667051')
        appointments = student['notifications']['appointment']
        assert len(appointments) == 5

    def test_appointment_marked_read(self, app, client, fake_auth):
        """Includes flag indicating whether user has seen each appointment."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            student_sid = '11667051'
            fake_auth.login(coe_scheduler_uid)
            response = client.post(
                '/api/appointments/create',
                data=json.dumps({
                    'deptCode': 'COENG',
                    'sid': student_sid,
                    'appointmentType': 'Drop-in',
                    'topics': ['Topic for appointments, 4'],
                }),
                content_type='application/json',
            )
            assert response.status_code == 200
            boa_appointment_id = response.json['id']

            def _is_appointment_read(appointment_id):
                student = self._api_student_by_sid(client=client, sid=student_sid)
                appointments = student['notifications']['appointment']
                appointment = next((a for a in appointments if a['id'] == appointment_id), None)
                assert appointment is not None
                return appointment.get('read') is True

            fake_auth.login(asc_advisor_uid)
            assert _is_appointment_read(boa_appointment_id) is False
            client.post(f'/api/appointments/{boa_appointment_id}/mark_read')
            assert _is_appointment_read(boa_appointment_id) is True

            legacy_appointment_id = '11667051-00010'
            assert _is_appointment_read(legacy_appointment_id) is False
            client.post(f'/api/appointments/{legacy_appointment_id}/mark_read')
            assert _is_appointment_read(legacy_appointment_id) is True


class TestAlerts:

    admin_uid = '2040'

    @classmethod
    def _get_alerts(cls, client, uid):
        response = client.get(f'/api/student/by_uid/{uid}')
        assert response.status_code == 200
        return response.json['notifications']['alert']

    def test_current_alerts_for_sid(self, create_alerts, fake_auth, client):
        """Returns current_user's current alerts for a given sid."""
        fake_auth.login(self.admin_uid)
        alerts = self._get_alerts(client, 61889)
        assert len(alerts) == 4
        assert alerts[0]['alertType'] == 'academic_standing'
        assert alerts[0]['key'] == '2178_2017-12-30_academic_standing_PRO'
        assert alerts[0]['message'] == "Student's academic standing is 'Probation'."
        assert not alerts[0]['dismissed']

        assert alerts[1]['alertType'] == 'late_assignment'
        assert alerts[1]['key'] == '2178_800900300'
        assert alerts[1]['message'] == 'Week 5 homework in RUSSIAN 13 is late.'
        assert not alerts[1]['dismissed']

        assert alerts[2]['alertType'] == 'missing_assignment'
        assert alerts[2]['key'] == '2178_500600700'
        assert alerts[2]['message'] == 'Week 6 homework in PORTUGUESE 12 is missing.'
        assert not alerts[2]['dismissed']

        assert alerts[3]['alertType'] == 'midterm'
        assert alerts[3]['key'] == '2178_90100'
        assert alerts[3]['message'] == 'BURMESE 1A midpoint deficient grade of D+.'
        assert not alerts[3]['dismissed']


class TestPrefixSearch:

    def test_require_login(self, client):
        response = client.get('/api/students/find_by_name_or_sid?q=Paul')
        assert response.status_code == 401

    def test_student_prefix_search_by_name(self, client, coe_advisor_login):
        """When searching by name, results include current students only."""
        response = client.get('/api/students/find_by_name_or_sid?q=Paul')
        assert response.status_code == 200
        assert len(response.json) == 3
        labels = [s['label'] for s in response.json]
        assert 'Paul Farestveit (7890123456)' in labels
        assert 'Paul Kerschen (3456789012)' in labels
        assert "Wolfgang Pauli-O'Rourke (9000000000)" in labels

    def test_student_prefix_search_by_sid(self, client, coe_advisor_login):
        """When searching by SID, results include both current and non-current students."""
        response = client.get('/api/students/find_by_name_or_sid?q=9')
        assert response.status_code == 200
        assert len(response.json) == 3
        labels = [s['label'] for s in response.json]
        assert "Wolfgang Pauli-O'Rourke (9000000000)" in labels
        assert 'Nora Stanton Barney (9100000000)' in labels
        assert 'Paul Tarsus (9191919191)' in labels

    def test_allow_scheduler(self, client, coe_scheduler_login):
        response = client.get('/api/students/find_by_name_or_sid?q=Paul')
        assert response.status_code == 200
        assert len(response.json) == 3


class TestNotes:
    """Advising Notes API."""

    def test_advising_note(self, client, mock_advising_note, fake_auth):
        """Returns a BOAC-created note."""
        author_uid = mock_advising_note.author_uid
        fake_auth.login(author_uid)
        response = client.get('/api/student/by_uid/61889')
        assert response.status_code == 200
        assert 'appointments' not in response.json
        notes = response.json.get('notifications', {}).get('note')
        assert len(notes)
        note = next((n for n in notes if n.get('subject') == 'In France they kiss on main street'), None)
        assert len(note)
        assert 'My darling dime store thief' in note['message']
        author = note['author']
        assert author['name'] == 'Joni Mitchell CC'
        assert author['role'] == 'Director'
        assert author['departments'][0]['name'] == 'Athletic Study Center'
        # This note was not authored by coe_advisor_uid
        assert author['uid'] == author_uid

    def test_legacy_advising_note(self, client, fake_auth):
        """Returns a legacy note."""
        coe_advisor_uid = '1133399'
        fake_auth.login(coe_advisor_uid)
        response = client.get('/api/student/by_uid/61889')
        assert response.status_code == 200
        notes = response.json.get('notifications', {}).get('note')
        assert len(notes)
        note = next((n for n in notes if n.get('id') == '11667051-00001'), None)
        assert len(note)
        assert note['legacySource'] == 'SIS'
        assert 'Brigitte is making athletic and moral progress' == note['message']
        author = note['author']
        assert not author['name']
        assert not author['role']
        assert not len(author['departments'])
        advisor_sid = '800700600'
        assert author['sid'] == advisor_sid


class TestDistinctSids:

    @classmethod
    def _api_distinct_sids(
            cls,
            client,
            sids=(),
            cohort_ids=(),
            curated_group_ids=(),
            expected_status_code=200,
    ):
        response = client.post(
            '/api/students/distinct_sids',
            data=json.dumps({
                'sids': sids,
                'cohortIds': cohort_ids,
                'curatedGroupIds': curated_group_ids,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_distinct_sids_not_authenticated(self, client):
        """Deny anonymous access to batch note metadata."""
        self._api_distinct_sids(
            client,
            sids=['11667051'],
            cohort_ids=[1, 2],
            expected_status_code=401,
        )

    def test_distinct_sids_not_owner(self, client, fake_auth):
        """Deny user access to cohort owned by some other dept."""
        user_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        cohorts = CohortFilter.get_cohorts(user_id)
        # Assert non-zero student count
        assert sum(list(map(lambda c: c['totalStudentCount'], cohorts)))
        # Log in as non-owner
        fake_auth.login(asc_advisor_uid)
        cohort_ids = [c['id'] for c in cohorts]
        assert self._api_distinct_sids(client, cohort_ids=cohort_ids)['sids'] == []

    def test_distinct_sids(self, client, fake_auth):
        """Get distinct SIDs across cohorts and curated groups."""
        user_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        cohort_ids = []
        sids = set()
        for cohort in CohortFilter.get_cohorts(user_id):
            cohort_id = cohort['id']
            cohort_ids.append(cohort_id)
            sids.update(set(CohortFilter.get_sids(cohort_id)))

        assert len(sids) > 1
        curated_group = CuratedGroup.create(user_id, 'Like a lemon to a lime, a lime to a lemon')
        curated_group_ids = [curated_group.id]
        # We use SIDs from cohorts (above). Therefore, we expect no increase in 'batch_distinct_student_count'.
        for sid in sids:
            CuratedGroup.add_student(curated_group.id, sid)
        # A specific student (SID) that is in neither cohorts nor curated groups.
        some_other_sid = '5678901234'
        assert some_other_sid not in sids
        # Log in as authorized user
        fake_auth.login(coe_advisor_uid)
        data = self._api_distinct_sids(
            client,
            cohort_ids=cohort_ids,
            curated_group_ids=curated_group_ids,
            sids=[some_other_sid],
        )
        assert sids.union({some_other_sid}) == set(data['sids'])


class TestFindBySids:
    """Find students by SIDs."""

    @staticmethod
    def _api_find_by_sids(client, sids=(), expected_status_code=200):
        response = client.post(
            '/api/students/by_sids',
            content_type='application/json',
            data=json.dumps({
                'sids': sids,
            }),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Requires authentication."""
        self._api_find_by_sids(client, expected_status_code=401)

    def test_missing_param(self, client, coe_advisor_login):
        """Requires list of SIDs."""
        self._api_find_by_sids(client, expected_status_code=400)

    def test_invalid_param(self, client, coe_advisor_login):
        """Requires SIDs to be numeric."""
        self._api_find_by_sids(
            client,
            sids=[123, '456', 'abc'],
            expected_status_code=400,
        )

    def test_(self, client, coe_advisor_login):
        """Returns basic attributes for SIDs found."""
        api_json = self._api_find_by_sids(
            client,
            sids=['9000000000', '9999999999', '9100000000'],
            expected_status_code=200,
        )
        assert len(api_json) == 2
        assert api_json[0]['label'] == 'Wolfgang Pauli-O\'Rourke (9000000000)'
        assert api_json[0]['sid'] == '9000000000'
        assert api_json[0]['uid'] == '300847'
        assert api_json[1]['label'] == 'Nora Stanton Barney (9100000000)'
        assert api_json[1]['sid'] == '9100000000'
        assert api_json[1]['uid'] == '300848'


class TestValidateSids:
    """Student API."""

    @staticmethod
    def _api_validate_sids(client, sids=(), expected_status_code=200):
        response = client.post(
            '/api/students/validate_sids',
            content_type='application/json',
            data=json.dumps({
                'sids': sids,
            }),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_validate_sids_not_authenticated(self, client):
        """Requires authentication."""
        self._api_validate_sids(client, expected_status_code=401)

    def test_scheduler_cannot_validate_sids(self, client, coe_scheduler_login):
        """Scheduler cannot validate SIDs."""
        self._api_validate_sids(client, expected_status_code=401)

    def test_validate_sids_with_invalid_sid(self, client, coe_advisor_login):
        """Complains about non-numeric SID."""
        self._api_validate_sids(client, sids=['7890123456', 'ABC'], expected_status_code=400)

    def test_validate_sids_with_some_invalid(self, client, coe_advisor_login):
        """SID status is 404 if student is not found."""
        api_json = self._api_validate_sids(
            client,
            sids=['7890123456', '9999999999', '2345678901'],
            expected_status_code=200,
        )
        assert len(api_json) == 3
        assert api_json[0]['sid'] == '7890123456'
        assert api_json[0]['status'] == 200
        assert api_json[1]['sid'] == '9999999999'
        assert api_json[1]['status'] == 404
        assert api_json[2]['sid'] == '2345678901'
        assert api_json[2]['status'] == 200

    def test_validate_sids_with_some_inactive(self, client, coe_advisor_login):
        """Accepts inactive SIDs."""
        api_json = self._api_validate_sids(client, sids=['7890123456', '2718281828', '3141592653'])
        assert len(api_json) == 3
        assert [a['status'] for a in api_json] == [200, 200, 200]

    def test_validate_sids_by_admin(self, client, admin_login):
        """Admin has access to all students."""
        api_json = self._api_validate_sids(
            client,
            sids=['11667051', '2345678901'],
            expected_status_code=200,
        )
        assert len(api_json) == 2
        assert api_json[0]['sid'] == '11667051'
        assert api_json[0]['status'] == 200
        assert api_json[1]['sid'] == '2345678901'
        assert api_json[1]['status'] == 200


def _get_common_sids(student_list_1, student_list_2):
    sid_list_1 = [s['sid'] for s in student_list_1]
    sid_list_2 = [s['sid'] for s in student_list_2]
    return list(set(sid_list_1) & set(sid_list_2))
