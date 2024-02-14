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

from boac.factory import create_app
from pprintpp import pprint as pp # noqa

"""Run Flask-wrapped code from a Python console.

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
                        created=2018-01-12 11:02:35.536011,
                        deleted_at=None>
                    , ...

"""

app = create_app()
ac = app.app_context()
ac.push()

print('You are now in a Flask app context. To run normal app teardown processes, type:')
print('   ac.pop()')
