"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.externals import calnet
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.models.json_cache import stow


@stow('calnet_user_for_uid_{uid}')
def get_calnet_user_for_uid(app, uid, force_feed=True):
    persons = calnet.client(app).search_uids([uid])
    if not persons and not force_feed:
        return None
    return {
        **_calnet_user_api_feed(persons[0] if len(persons) else None),
        **{'uid': uid},
    }


@stow('calnet_user_for_csid_{csid}')
def get_calnet_user_for_csid(app, csid):
    persons = calnet.client(app).search_csids([csid])
    return {
        **_calnet_user_api_feed(persons[0] if len(persons) else None),
        **{'csid': csid},
    }


def get_calnet_users_for_csids(app, csids):
    persons = calnet.client(app).search_csids(csids)
    return {person['csid']: _calnet_user_api_feed(person) for person in persons}


def _calnet_user_api_feed(person):
    def _get(key):
        return person and person[key]
    # Array of departments is compatible with BOAC user schema.
    departments = []
    dept_code = _get_dept_code(person)
    if dept_code:
        departments.append({
            'code': dept_code,
            'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code) if dept_code in BERKELEY_DEPT_CODE_TO_NAME else dept_code,
        })
    return {
        'campusEmail': _get('campus_email'),
        'departments': departments,
        'email': _get('email'),
        'firstName': _get('first_name'),
        'lastName': _get('last_name'),
        'name': _get('name'),
        'csid': _get('csid'),
        'title': _get('title'),
        'uid': _get('uid'),
    }


def _get_dept_code(p):
    def dept_code_fallback():
        dept_hierarchy = p['dept_unit_hierarchy']
        if dept_hierarchy:
            dept_hierarchy = dept_hierarchy[0] if isinstance(dept_hierarchy, list) else dept_hierarchy
            return dept_hierarchy.rsplit('-', 1)[-1] if dept_hierarchy else None
        else:
            return None
    return p and (p['primary_dept_code'] or p['dept_code'] or p['calnet_dept_code'] or dept_code_fallback())
