"""Official access to team memberships"""

from boac.lib import http
from flask import current_app as app


def get_team(sport):
    url = f"{app.config['ATHLETE_API_URL']}/sport/{sport}"
    return authorized_request(url)


def list_sports():
    query = {
        'field-name': 'athleteSport.sport',
    }
    url = http.build_url(f"{app.config['ATHLETE_API_URL']}/descriptors", query)
    return authorized_request(url)


def authorized_request(url):
    auth_headers = {
        'app_id': app.config['ATHLETE_API_ID'],
        'app_key': app.config['ATHLETE_API_KEY'],
        'Accept': 'application/json',
    }
    return http.request(url, auth_headers)
