import csv
from boac import db
from boac.models.authorized_user import AuthorizedUser
# Needed for db.create_all to find the model.
from boac.models.team import Team # noqa
from boac.models.json_cache import JsonCache # noqa


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
    for row in csv_reader:
        obj = AuthorizedUser(**row)
        db.session.add(obj)
    db.session.commit()


if __name__ == '__main__':
    import boac.factory
    boac.factory.create_app()
    load()
