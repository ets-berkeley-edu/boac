"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


"""Official access to team memberships."""

from boac.lib import http
from boac.models.json_cache import stow
from flask import current_app as app


@stow('athletes_team_{sport}')
def get_team(sport):
    url = '{url}/sport/{sport}'.format(url=app.config['ATHLETE_API_URL'], sport=sport)
    response = authorized_request(url)
    if response and hasattr(response, 'json'):
        return response.json().get('apiResponse', {}).get('response', {}).get('athletes', {}).get('athlete', [])
    else:
        return


@stow('athletes_sports')
def list_sports():
    query = {
        'field-name': 'athleteSport.sport',
    }
    url = http.build_url('{url}/descriptors'.format(url=app.config['ATHLETE_API_URL']), query)
    response = authorized_request(url)
    if response and hasattr(response, 'json'):
        unwrapped = response.json().get('apiResponse', {}).get('response', {}).get('fieldValueLists', {}).get('fieldValueLists', [])
        if unwrapped:
            unwrapped = unwrapped[0].get('fieldValues', [])
        return unwrapped
    else:
        return


def authorized_request(url):
    auth_headers = {
        'app_id': app.config['ATHLETE_API_ID'],
        'app_key': app.config['ATHLETE_API_KEY'],
        'Accept': 'application/json',
    }
    return http.request(url, auth_headers)
