import csv
from boac import db
from boac.models.athletics import Athletics
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
# Needed for db.create_all to find the model.
from boac.models.json_cache import JsonCache # noqa
from boac.models.student import Student


_default_users_csv = """uid,is_admin,is_director,is_advisor
2040,true,false,false
53791,true,false,false
95509,true,false,false
177473,true,false,false
1133399,true,false,false
211159,true,false,false
242881,true,false,false
1022796,true,false,false
"""

brigitte = {
    'uid': '61889',
    'sid': '11667051',
    'first_name': 'Brigitte',
    'last_name': 'Lin',
    'in_intensive_cohort': True,
}
john = {
    'uid': '1022796',
    'sid': '8901234567',
    'first_name': 'John',
    'last_name': 'Crossman',
    'in_intensive_cohort': False,
}
oliver = {
    'uid': '2040',
    'sid': '2345678901',
    'first_name': 'Oliver',
    'last_name': 'Heyer',
    'in_intensive_cohort': False,
}
paul = {
    'uid': '242881',
    'sid': '3456789012',
    'first_name': 'Paul',
    'last_name': 'Kerschen',
    'in_intensive_cohort': True,
}
sandeep = {
    'uid': '1133399',
    'sid': '5678901234',
    'first_name': 'Sandeep',
    'last_name': 'Jayaprakash',
    'in_intensive_cohort': False,
}
football_defensive_backs = {
    'asc_sport_code_core': 'MFB',
    'group_code': 'MFB-DB',
    'group_name': 'Football, Defensive Backs',
    'team_code': 'FBM',
    'team_name': 'Football',
}
football_defensive_line = {
    'asc_sport_code_core': 'MFB',
    'group_code': 'MFB-DL',
    'group_name': 'Football, Defensive Line',
    'team_code': 'FBM',
    'team_name': 'Football',
}
womens_field_hockey = {
    'asc_sport_code_core': 'WFH',
    'group_code': 'WFH-AA',
    'group_name': 'Women\'s Field Hockey',
    'team_code': 'FHW',
    'team_name': 'Women\'s Field Hockey',
}
mens_tennis = {
    'asc_sport_code_core': 'MTE',
    'group_code': 'MTE-AA',
    'group_name': 'Men\'s Tennis',
    'team_code': 'TNM',
    'team_name': 'Men\'s Tennis',
}
womens_tennis = {
    'asc_sport_code_core': 'WTE',
    'group_code': 'WTE-AA',
    'group_name': 'Women\'s Tennis',
    'team_code': 'TNW',
    'team_name': 'Women\'s Tennis',
}


def clear():
    db.drop_all()


def load(cohort_test_data=False):
    load_schemas()
    load_development_data()
    if cohort_test_data:
        load_student_athletes()
        load_cohorts()
    return db


def load_schemas():
    """
    During early development, create the test DB from Python code.
    We will convert to SQL scripts before enabling production deployments.
    """
    db.create_all()


def load_development_data():
    csv_reader = csv.DictReader(_default_users_csv.splitlines())
    for row in csv_reader:
        # This script can be run more than once. Do not create user if s/he exists in BOAC db.
        user = AuthorizedUser.find_by_uid(row['uid'])
        if not user:
            user = AuthorizedUser(**row)
            db.session.add(user)
    db.session.commit()


def create_team_group(t):
    athletics = Athletics(group_code=t['group_code'], group_name=t['group_name'], team_code=t['team_code'],
                          team_name=t['team_name'])
    db.session.add(athletics)
    return athletics


def assign_athletes(student, team_groups):
    student = Student(
        sid=student['sid'],
        uid=student['uid'],
        first_name=student['first_name'],
        last_name=student['last_name'],
        in_intensive_cohort=student['in_intensive_cohort'],
    )
    db.session.add(student)
    for team_group in team_groups:
        team_group.athletes.append(student)


def load_student_athletes():
    _football_defensive_backs = create_team_group(football_defensive_backs)
    _football_defensive_line = create_team_group(football_defensive_line)
    _men_tennis = create_team_group(mens_tennis)
    _women_field_hockey = create_team_group(womens_field_hockey)
    _women_tennis = create_team_group(womens_tennis)

    # Assign athletes
    assign_athletes(brigitte, [_women_field_hockey, _women_tennis])
    assign_athletes(john, [])
    assign_athletes(oliver, [_football_defensive_backs, _football_defensive_line])
    assign_athletes(paul, [_football_defensive_line])
    assign_athletes(sandeep, [_football_defensive_backs, _football_defensive_line, _men_tennis])

    db.session.commit()


def load_cohorts():
    # Oliver's cohorts
    CohortFilter.create(label='All sports', team_group_codes=['MFB-DL', 'MFB-DL', 'WFH-AA'], uid='2040')
    CohortFilter.create(label='Football, Defense', team_group_codes=['MFB-DL', 'MFB-DL'], uid='2040')
    CohortFilter.create(label='Field Hockey', team_group_codes=['WFH-AA'], uid='2040')
    # Sandeep's cohorts
    CohortFilter.create(label='All sports', team_group_codes=['MFB-DL', 'MFB-DL', 'WFH-AA'], uid='1133399')
    CohortFilter.create(label='Football, Defense Backs', team_group_codes=['MFB-DB'], uid='1133399')
    db.session.commit()


if __name__ == '__main__':
    import boac.factory
    boac.factory.create_app()
    load()
