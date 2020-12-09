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

from boac.api.errors import InternalServerError
from boac.externals import calnet
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.models.json_cache import fetch_bulk, insert_row, stow


@stow('calnet_user_for_uid_{uid}')
def get_calnet_user_for_uid(app, uid, force_feed=True, skip_expired_users=False):
    if skip_expired_users:
        persons = calnet.client(app).search_uids([uid])
    else:
        for search_expired in (False, True):
            persons = calnet.client(app).search_uids([uid], search_expired)
            if persons:
                break
    if not persons and not force_feed:
        return None
    return {
        **_calnet_user_api_feed(persons[0] if len(persons) else None),
        **{'uid': uid},
    }


@stow('calnet_user_for_csid_{csid}')
def get_calnet_user_for_csid(app, csid):
    for search_expired in (False, True):
        persons = calnet.client(app).search_csids([csid], search_expired)
        if persons:
            break
    return {
        **_calnet_user_api_feed(persons[0] if len(persons) else None),
        **{'csid': csid},
    }


def get_calnet_users_for_uids(app, uids):
    return _get_calnet_users(app, 'uid', uids)


def get_calnet_users_for_csids(app, csids):
    return _get_calnet_users(app, 'csid', csids)


def get_csid_for_uid(app, uid):
    user_feed = get_calnet_user_for_uid(app, uid)
    if user_feed:
        return user_feed.get('csid')


def get_uid_for_csid(app, csid):
    user_feed = get_calnet_user_for_csid(app, csid)
    if user_feed:
        return user_feed.get('uid')


def _get_calnet_users(app, id_type, ids):
    cached_users = fetch_bulk([f'calnet_user_for_{id_type}_{_id}' for _id in ids])
    users_by_id = {k.replace(f'calnet_user_for_{id_type}_', ''): v for k, v in cached_users.items()}
    uncached_ids = [c for c in ids if c not in users_by_id]
    calnet_client = calnet.client(app)
    if id_type == 'uid':
        calnet_results = calnet_client.search_uids(uncached_ids)
    elif id_type == 'csid':
        calnet_results = calnet_client.search_csids(uncached_ids)
    else:
        raise InternalServerError(f'get_calnet_users: {id_type} is an invalid id type')
    # Cache rows individually so that an isolated conflict doesn't sink the rest of the update.
    for _id in uncached_ids:
        calnet_result = next((r for r in calnet_results if r[id_type] == _id), None)
        feed = {
            **_calnet_user_api_feed(calnet_result),
            **{id_type: _id},
        }
        insert_row(f'calnet_user_for_{id_type}_{_id}', feed)
        users_by_id[_id] = feed
    return users_by_id


def _calnet_user_api_feed(person):
    def _get(key):
        return _get_attribute(person, key)
    # Array of departments is compatible with BOAC user schema.
    departments = []
    dept_code = _get_dept_code(person)
    if dept_code:
        departments.append({
            'code': dept_code,
            'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code, dept_code),
        })
    return {
        'campusEmail': _get('campus_email'),
        'departments': departments,
        'email': _get('email'),
        'firstName': _get('first_name'),
        'isExpiredPerLdap': _get('expired'),
        'lastName': _get('last_name'),
        'name': _get('name'),
        'csid': _get('csid'),
        'title': _get('title'),
        'uid': _get('uid'),
    }


def _get_dept_code(p):
    return p and (p['primary_dept_code'] or p['dept_code'])


def _get_attribute(person, key):
    if not person:
        return None
    elif isinstance(person[key], list):
        return person[key][0]
    else:
        return person[key]
