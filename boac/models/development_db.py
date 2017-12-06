import csv
from boac import db
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
# Needed for db.create_all to find the model.
from boac.models.json_cache import JsonCache # noqa
from boac.models.team_member import TeamMember # noqa


def clear():
    db.drop_all()


def load(cohort_test_data=False):
    load_schemas()
    load_development_data()
    if cohort_test_data:
        load_cohort_test_data()
    return db


def load_schemas():
    """
    During early development, create the test DB from Python code.
    We will convert to SQL scripts before enabling production deployments.
    """
    db.create_all()


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


def load_development_data():
    csv_reader = csv.DictReader(_default_users_csv.splitlines())
    for row in csv_reader:
        # This script can be run more than once. Do not create user if s/he exists in BOAC db.
        user = AuthorizedUser.find_by_uid(row['uid'])
        if not user:
            user = AuthorizedUser(**row)
            db.session.add(user)
    db.session.commit()


def add_team_member(sport, student):
    db.session.add(TeamMember(code=sport['code'],
                              asc_sport_code_core=sport['asc_sport_code_core'],
                              asc_sport_core=sport['asc_sport_core'],
                              asc_sport_code=sport['asc_sport_code'],
                              asc_sport=sport['asc_sport'],
                              member_uid=student['member_uid'],
                              member_csid=student['member_csid'],
                              member_name=student['member_name']))


def load_cohort_test_data():
    brigitte = {
        'member_uid': '61889',
        'member_csid': '11667051',
        'member_name': 'Brigitte Lin',
    }
    oliver = {
        'member_uid': '2040',
        'member_csid': '2345678901',
        'member_name': 'Oliver Heyer',
    }
    paul = {
        'member_uid': '242881',
        'member_csid': '3456789012',
        'member_name': 'Paul Kerschen',
    }
    sandeep = {
        'member_uid': '1133399',
        'member_csid': '5678901234',
        'member_name': 'Sandeep Jayaprakash',
    }
    football_defensive_backs = {
        'code': 'FBM',
        'asc_sport_code_core': 'MFB',
        'asc_sport_core': 'Football',
        'asc_sport_code': 'MFB-DB',
        'asc_sport': 'Football, Defensive Backs',
    }
    football_defensive_line = {
        'code': 'FBM',
        'asc_sport_code_core': 'MFB',
        'asc_sport_core': 'Football',
        'asc_sport_code': 'MFB-DL',
        'asc_sport': 'Football, Defensive Line',
    }
    womens_field_hockey = {
        'code': 'FHW',
        'asc_sport_code_core': 'WFH',
        'asc_sport_core': 'Women\'s Field Hockey',
        'asc_sport_code': 'WFH-AA',
        'asc_sport': 'Women\'s Field Hockey',
    }
    mens_tennis = {
        'code': 'TNM',
        'asc_sport_code_core': 'MTE',
        'asc_sport_core': 'Men\'s Tennis',
        'asc_sport_code': 'MTE-AA',
        'asc_sport': 'Men\'s Tennis',
    }
    womens_tennis = {
        'code': 'TNW',
        'asc_sport_code_core': 'WTE',
        'asc_sport_core': 'Women\'s Tennis',
        'asc_sport_code': 'WTE-AA',
        'asc_sport': 'Women\'s Tennis',
    }
    # Assign athletes
    add_team_member(womens_field_hockey, brigitte)
    add_team_member(womens_tennis, brigitte)
    add_team_member(football_defensive_backs, oliver)
    add_team_member(football_defensive_line, oliver)
    add_team_member(football_defensive_line, paul)
    add_team_member(football_defensive_line, sandeep)
    add_team_member(mens_tennis, sandeep)
    add_team_member(football_defensive_line, sandeep)

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
