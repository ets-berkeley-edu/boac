"""Official access to team memberships"""

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
