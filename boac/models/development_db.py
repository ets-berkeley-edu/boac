import csv
from boac import db
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
# Needed for db.create_all to find the model.
from boac.models.json_cache import JsonCache # noqa
from boac.models.team_member import TeamMember # noqa


def clear():
    db.drop_all()


def load():
    load_schemas()
    load_development_data()
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
    team_codes = list(TeamMember.team_definitions.keys())
    # Sort for deterministic order
    team_codes.sort()
    for row in csv_reader:
        # This script can be run more than once. Do not create user if s/he exists in BOAC db.
        user = AuthorizedUser.find_by_uid(row['uid'])
        if not user:
            user = AuthorizedUser(**row)
            db.session.add(user)

        # Random UIDs get test data (saved cohorts)
        if '1' in user.uid:
            next_codes = [team_codes.pop(), team_codes.pop(), team_codes.pop(), team_codes.pop()]
            for team_code in next_codes:
                create_team_members(db.session, team_code)

            create_cohort(next_codes[0], next_codes[1], user.uid)
            create_cohort(next_codes[2], next_codes[3], user.uid)

    db.session.add(TeamMember(code='FHW', member_uid='61889', member_csid='11667051', member_name='Brigitte Lin'))

    db.session.commit()


def create_cohort(team_code1, team_code2, uid):
    name1 = TeamMember.team_definitions[team_code1]
    name2 = TeamMember.team_definitions[team_code2]
    CohortFilter.create(label=name1 + ' and ' + name2, team_codes=[team_code1, team_code2], uid=uid)


def create_team_members(db_session, team_code):
    team_members = [
        TeamMember(code=team_code, member_uid='111', member_csid='1111', member_name='Lin, Brigitte'),
        TeamMember(code=team_code, member_uid='222', member_csid='2222', member_name='Garza, Isabel'),
        TeamMember(code=team_code, member_uid='333', member_csid='3333', member_name='Cooper, Terry'),
    ]
    for team_member in team_members:
        db_session.add(team_member)


if __name__ == '__main__':
    import boac.factory
    boac.factory.create_app()
    load()
