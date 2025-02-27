"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.util import can_access_admitted_students, is_peer_advisor, is_peer_advisor_manager
from boac.lib.util import has_any_membership_role
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.routes import login_manager
from flask import current_app as app, request
from flask_login import current_user


def admin_or_director_required(func):
    @wraps(func)
    def _admin_or_director_required(*args, **kw):
        is_authorized = current_user.is_authenticated and (
            current_user.is_admin
            or (current_user.is_authenticated and has_any_membership_role(current_user, 'director'))
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _admin_or_director_required


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        is_authorized = current_user.is_authenticated and current_user.is_admin
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _admin_required


def advising_data_access_required(func):
    @wraps(func)
    def _advising_data_access_required(*args, **kw):
        is_authorized = (
            current_user.is_authenticated
            and current_user.can_access_advising_data
            and (current_user.is_admin or has_any_membership_role(current_user, 'advisor', 'director'))
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _advising_data_access_required


def advisor_or_peer_advisor_required(func):
    @wraps(func)
    def _advisor_required(*args, **kw):
        if (current_user.is_authenticated and (
            current_user.is_admin
            or has_any_membership_role(current_user, 'advisor', 'director')
            or is_peer_advisor(current_user)
            or _api_key_ok()
        )):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _advisor_required


def advisor_required(func):
    @wraps(func)
    def _advisor_required(*args, **kw):
        if current_user.is_admin or has_any_membership_role(current_user, 'advisor', 'director') or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _advisor_required


def can_edit_degree_progress(func):
    @wraps(func)
    def _qualifies(*args, **kw):
        if (current_user.is_authenticated and current_user.can_edit_degree_progress) or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _qualifies


def can_read_degree_progress(func):
    @wraps(func)
    def _qualifies(*args, **kw):
        if (current_user.is_authenticated and current_user.can_read_degree_progress) or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _qualifies


def ce3_required(func):
    @wraps(func)
    def _ce3_required(*args, **kw):
        is_authorized = can_access_admitted_students(current_user)
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _ce3_required


def director_advising_data_access_required(func):
    @wraps(func)
    def _director_advising_data_access_required(*args, **kw):
        is_authorized = (
            current_user.is_authenticated
            and current_user.can_access_advising_data
            and (current_user.is_admin or has_any_membership_role(current_user, 'director'))
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _director_advising_data_access_required


def peer_advisor_manager_required(func):
    @wraps(func)
    def _advisor_required(*args, **kw):
        if (
            current_user.is_authenticated
            and (
                current_user.is_admin
                or is_peer_advisor_manager(current_user)
                or _api_key_ok()
            )
        ):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _advisor_required


def peer_advisor_or_peer_advisor_manager(func):
    @wraps(func)
    def _peer_advisor_or_peer_advisor_manager(*args, **kw):
        if current_user.is_authenticated and (
                current_user.is_admin
                or is_peer_advisor_manager(current_user)
                or is_peer_advisor(current_user)
                or _api_key_ok()
        ):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _peer_advisor_or_peer_advisor_manager


def peer_advisor_or_peer_advisor_manager_in_department(func):
    # Checks if the peer_advisor or peer_advisor_manager is in the peer_advising_department in the URL parameter
    @wraps(func)
    def _peer_advisor_or_manager_in_department(*args, **kw):
        # Extract the peer_advising_department_id from the URL params
        peer_advising_department_id = kw.get('peer_advising_department_id') or request.view_args.get(
            'peer_advising_department_id')
        if peer_advising_department_id is None:
            app.logger.error('Department ID missing in URL.')
            return login_manager.unauthorized()
        if (current_user.is_authenticated
                and (
                    current_user.is_admin
                    or is_peer_advisor_manager(current_user)
                    or is_peer_advisor(current_user)
                    or _api_key_ok())
                and (
                    PeerAdvisingDepartmentMember.is_user_in_peer_advising_department(
                        user_id=current_user.get_id(),
                        peer_advising_department_id=peer_advising_department_id)
                )):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _peer_advisor_or_manager_in_department


def peer_advisor_required(func):
    @wraps(func)
    def _authorize(*args, **kw):
        if current_user.is_authenticated and (is_peer_advisor(current_user) or _api_key_ok()):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return login_manager.unauthorized()
    return _authorize


def _api_key_ok():
    auth_key = app.config['API_KEY']
    return auth_key and (request.headers.get('App-Key') == auth_key)
