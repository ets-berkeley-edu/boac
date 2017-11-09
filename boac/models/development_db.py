import csv
from boac import db
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user import CohortFilter
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
    cohort_filter_crew = create_cohort_filter('Men and women\'s crew', 'CRM', 'CRW')
    cohort_filter_soccer = create_cohort_filter('Men and women\'s soccer', 'SCW', 'SCM')
    for row in csv_reader:
        user = AuthorizedUser(**row)
        db.session.add(user)
        uid = int(user.uid)
        # A subset of users get one or more cohort_filters
        if uid > 100000:
            # The 'crew' and 'soccer' cohort_filters are both shared by multiple users
            choose_crew = uid < 1000000
            cohort = cohort_filter_crew if choose_crew else cohort_filter_soccer
            user.cohort_filters.append(cohort)

    db.session.commit()


def create_cohort_filter(label, code1, code2):
    return CohortFilter(
        label=label,
        filter_criteria='{"teams": ["' + code1 + '", "' + code2 + '"]}',
    )


if __name__ == '__main__':
    import boac.factory
    boac.factory.create_app()
    load()
