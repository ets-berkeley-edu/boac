import json
from boac.externals import asc_athletes_api
from boac.lib.mockingbird import MockResponse, register_mock
from boac.merged import import_asc_athletes
from boac.models.athletics import Athletics
from boac.models.student import Student


def find_athlete(team, sid):
    return next(athlete for athlete in team.athletes if athlete.sid == sid)


def asc_data_row(sid, group_code, group_name, team_code, team_name, academic_yr, is_active, is_intensive='No', status=''):
    return {
        'SID': sid,
        'SportCode': group_code,
        'Sport': group_name,
        'SportCodeCore': team_code,
        'SportCore': team_name,
        'AcadYr': academic_yr,
        'ActiveYN': is_active,
        'IntensiveYN': is_intensive,
        'SportStatus': status,
    }


class TestImportAscAthletes:
    """Import ASC data."""

    def test_initial_assumptions(self, app):
        water_polo_team = Athletics.query.filter_by(group_code='MWP').first()
        assert water_polo_team is None
        football_backs = Athletics.query.filter_by(group_code='MFB-DB').first()
        assert len(football_backs.athletes) == 3
        # John starts without a team.
        assert Student.find_by_sid('8901234567').athletics == []
        # PaulK defends the line.
        assert Student.find_by_sid('3456789012').athletics[0].group_code == 'MFB-DL'
        # Sandeep is busy.
        assert len(Student.find_by_sid('5678901234').athletics) == 3
        # Siegfried is a mug at everything.
        inactor = Student.find_by_sid('838927492')
        assert not inactor.is_active_asc
        assert inactor.status_asc == 'Trouble'
        assert len(inactor.athletics) == 5

    def test_update_from_asc_api_fixture(self, app):
        status = import_asc_athletes.update_from_asc_api()
        water_polo_team = Athletics.query.filter_by(group_code='MWP').first()
        assert len(water_polo_team.athletes) == 1
        football_backs = Athletics.query.filter_by(group_code='MFB-DB').first()
        assert len(football_backs.athletes) == 1
        # John has been recruited.
        assert Student.find_by_sid('8901234567').athletics[0].group_code == 'MFB-DL'
        # PaulK has dropped out.
        assert Student.find_by_sid('3456789012') is None
        # Sandeep relaxed.
        assert len(Student.find_by_sid('5678901234').athletics) == 1
        # Siegfried caught hydrophobia.
        inactor = Student.find_by_sid('838927492')
        assert not inactor.is_active_asc
        assert inactor.status_asc == 'Beyond Aid'
        assert inactor.athletics[0].group_code == 'MWP'
        assert(not status['errors'])
        assert(not status['warnings'])
        counts = status['change_counts']
        assert counts['deleted_students'] == 1
        assert counts['deleted_memberships'] == 7
        assert counts['new_memberships'] == 2
        assert counts['new_team_groups'] == 1

    def test_update_safety_check(self, app):
        skinny_import = {
            '1166.3': {
                'SID': '5678901234',
                'AcadYr': '2017-18',
                'IntensiveYN': 'No',
                'SportCode': 'MTE',
                'SportCodeCore': 'MTE',
                'Sport': 'Men\'s Tennis',
                'SportCore': 'Men\'s Tennis',
                'ActiveYN': 'Yes',
                'SportStatus': 'Compete',
                'SyncDate': '2018-01-31',
            },
        }
        modified_response = MockResponse(200, {}, json.dumps(skinny_import))
        with register_mock(asc_athletes_api._get_current_feed, modified_response):
            with_check = import_asc_athletes.update_from_asc_api()
            assert with_check['errors'][0]
            assert with_check['change_counts']['deleted_students'] == 0
            without_check = import_asc_athletes.update_from_asc_api(force=True)
            assert without_check['change_counts']['deleted_students'] > 0

    def test_empty_import(self, app):
        """Gracefully handles empty dataset."""
        status = import_asc_athletes.load_student_athletes([])
        assert {0} == set(status.values())

    def test_students_on_multiple_teams(self, app):
        """Maps one student to more than one team."""
        jane_sid = '1234567890'
        polo_code = 'WWP'
        volleyball_code = 'WVB'
        asc_data = [
            asc_data_row(
                jane_sid,
                polo_code,
                'Women\'s Water Polo',
                'WWP',
                'Women\'s Water Polo',
                '2017-18',
                'Yes',
            ),
            asc_data_row(
                jane_sid,
                volleyball_code,
                'Women\'s Volleyball',
                'WVB',
                'Women\'s Volleyball',
                '2017-18',
                'Yes',
            ),
        ]
        # Run import script
        status = import_asc_athletes.load_student_athletes(asc_data)
        assert 2 == status['new_team_groups']
        assert 1 == status['new_students']
        assert 2 == status['new_memberships']
        # Verify results
        polo_team = Athletics.query.filter_by(group_code=polo_code).first()
        assert find_athlete(polo_team, jane_sid)
        volleyball_team = Athletics.query.filter_by(group_code=volleyball_code).first()
        assert find_athlete(volleyball_team, jane_sid)

    def test_student_inactive(self, app):
        """Only imports inactive students if they are assigned to a team."""
        jane_sid = '1234567890'
        polo_code = 'WWP'
        asc_data = [
            asc_data_row(
                jane_sid,
                polo_code,
                'Women\'s Water Polo',
                'WWP',
                'Women\'s Water Polo',
                '2017-18',
                'No',
                'Yes',
                status='Not Active',
            ),
            asc_data_row(
                '96',
                '',
                '',
                '',
                '',
                '2017-18',
                'No',
                'Yes',
                status='TvParty2nite',
            ),
        ]
        # Run import script
        status = import_asc_athletes.load_student_athletes(asc_data)
        assert 1 == status['new_students']
        saved_student = Student.find_by_sid(jane_sid)
        assert saved_student.is_active_asc is False
        assert saved_student.status_asc == 'Not Active'

    def test_student_half_active(self, app):
        """A student who is active on one team is considered an active athlete."""
        sid = '1234567890'
        asc_data = [
            asc_data_row(
                sid,
                'WWP',
                'Women\'s Water Polo',
                'WWP',
                'Women\'s Water Polo',
                '2017-18',
                'No',
                'Yes',
                status='Not Active',
            ),
            asc_data_row(
                sid,
                'WFH',
                'Women\'s Field Hockey',
                'WFH',
                'Women\'s Field Hockey',
                '2017-18',
                'Yes',
                'Yes',
                status='Practice',
            ),
            asc_data_row(
                sid,
                'WTE',
                'Women\'s Tennis',
                'WTE',
                'Women\'s Tennis',
                '2017-18',
                'No',
                'Yes',
                status='Not Squad',
            ),
        ]
        # Run import script
        status = import_asc_athletes.load_student_athletes(asc_data)
        assert 1 == status['new_students']
        saved_student = Student.find_by_sid(sid)
        assert saved_student.is_active_asc is True
        assert len(saved_student.athletics) == 1
        assert saved_student.athletics[0].group_code == 'WFH'

    def test_student_intensive(self, app):
        """Marks intensive status if set."""
        jane_sid = '1234567890'
        polo_code = 'WWP'
        asc_data = [
            asc_data_row(
                jane_sid,
                polo_code,
                'Women\'s Water Polo',
                'WWP',
                'Women\'s Water Polo',
                '2017-18',
                'Yes',
                'Yes',
            ),
        ]
        # Run import script
        status = import_asc_athletes.load_student_athletes(asc_data)
        assert 1 == status['new_students']
        saved_student = Student.find_by_sid(jane_sid)
        assert saved_student.in_intensive_cohort
        assert saved_student.is_active_asc is True
