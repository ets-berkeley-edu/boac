"""Run Flask-wrapped code from a Python Console

* From the command line:
    ``boac> python -i consoler.py``

* In PyCharm preferences, go to "Build, Execution, Deployment"
* For "Console", enable "Always show debug console"
* For "Python Console", enable "Add source roots to PYTHONPATH"
* Add this line to the starting script:
    ``runfile('consoler.py')``
* Save
* Click on "Python Console"
* Click the bug icon to start a debugging session:

>>> from boac.models.authorized_user import AuthorizedUser
>>> rows = AuthorizedUser.query.all()
>>> pp(rows)
[
    <AuthorizedUser 2040,
                        is_admin=True,
                        is_advisor=False,
                        is_director=False,
                        updated=2018-01-12 11:02:35.536022,
                        created=2018-01-12 11:02:35.536011>
                    , ...

"""

from boac.factory import create_app
from pprintpp import pprint as pp

app = create_app()
ac = app.app_context()
ac.push()

print('You are now in a Flask app context. To run normal app teardown processes, type:')
print('   ac.pop()')
