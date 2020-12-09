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


from functools import wraps

from boac.factory import create_app

"""Execute script functions in an app context."""


def in_app(func):
    @wraps(func)
    def _in_app_func(*args, **kw):
        app = create_app()
        ac = app.app_context()
        try:
            ac.push()
            kw['app'] = app
            func(*args, **kw)
        finally:
            ac.pop()
    return _in_app_func


def in_session_request(func):
    """Flask-SQLAlchemy requires a request context to do any DB work."""
    @wraps(func)
    def _in_session_request_func(*args, **kw):
        request_ctx = None
        app = create_app()
        ac = app.app_context()
        try:
            ac.push()
            request_ctx = app.test_request_context('/')
            request_ctx.push()
            kw['app'] = app
            func(*args, **kw)
        finally:
            if request_ctx:
                request_ctx.pop()
            ac.pop()
    return _in_session_request_func
