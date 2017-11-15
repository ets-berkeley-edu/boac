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
    for row in csv_reader:
        user = AuthorizedUser(**row)
        db.session.add(user)
        # A subset of users get saved cohorts
        if '1' in user.uid:
            create_cohort(team_codes.pop(), team_codes.pop(), user.uid)
            create_cohort(team_codes.pop(), team_codes.pop(), user.uid)

    db.session.commit()


def create_cohort(team_code1, team_code2, uid):
    name1 = TeamMember.team_definitions[team_code1]
    name2 = TeamMember.team_definitions[team_code2]
    CohortFilter.create(label=name1 + ' and ' + name2, team_codes=[team_code1, team_code2], uid=uid)


if __name__ == '__main__':
    import boac.factory
    boac.factory.create_app()
    load()
