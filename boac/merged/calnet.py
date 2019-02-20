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
from boac.models.json_cache import stow


@stow('calnet_user_for_uid_{uid}')
def get_calnet_user_for_uid(app, uid):
    persons = calnet.client(app).search_uids([uid])
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
    return {
        'uid': _get('uid'),
        'csid': _get('csid'),
        'firstName': _get('first_name'),
        'lastName': _get('last_name'),
    }
