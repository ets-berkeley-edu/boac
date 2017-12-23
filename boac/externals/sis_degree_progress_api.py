"""Official access to undergraduate degree progress"""

from boac.lib import http
from boac.lib.mockingbird import fixture
from boac.models.json_cache import stow
from flask import current_app as app
from requests.auth import HTTPBasicAuth
import xmltodict


def parsed_degree_progress(cs_id):
    data = {}
    cs_feed = get_degree_progress(cs_id)
    if cs_feed:
        requirements_list = cs_feed.get('UC_AA_PROGRESS', {}).get('PROGRESSES', {}).get('PROGRESS', {}).get('REQUIREMENTS', {}).get('REQUIREMENT')
        if requirements_list:
            data['reportDate'] = cs_feed['UC_AA_PROGRESS']['PROGRESSES']['PROGRESS']['RPT_DATE']
            data['requirements'] = {
                'entryLevelWriting': {'name': 'Entry Level Writing'},
                'americanHistory': {'name': 'American History'},
                'americanInstitutions': {'name': 'American Institutions'},
                'americanCultures': {'name': 'American Cultures'},
            }
            for req in requirements_list:
                merge_requirement_status(data['requirements'], req)
    return data


def merge_requirement_status(data, req):
    code = req.get('CODE')
    if code:
        code = int(req.get('CODE'))
        if code == 1:
            key = 'entryLevelWriting'
        elif code == 2:
            key = 'americanHistory'
        elif code == 3:
            key = 'americanCultures'
        elif code == 18:
            key = 'americanInstitutions'
        else:
            return
        if req.get('IN_PROGRESS') == 'Y':
            status = 'In Progress'
        elif req.get('STATUS') == 'COMP':
            status = 'Satisfied'
        else:
            status = 'Not Satisfied'
        data[key]['status'] = status


@stow('sis_degree_progress_api_{cs_id}')
def get_degree_progress(cs_id):
    response = _get_degree_progress(cs_id)
    if response:
        de_xmled = xmltodict.parse(response.text)
        if de_xmled.get('UC_AA_PROGRESS'):
            return de_xmled
        else:
            return False
    else:
        if hasattr(response, 'raw_response') and hasattr(response.raw_response, 'status_code') and response.raw_response.status_code == 404:
            return False
        else:
            return None


@fixture('sis_degree_progress_{cs_id}.xml')
def _get_degree_progress(cs_id, mock=None):
    url = http.build_url(app.config['DEGREE_PROGRESS_API_URL'], {'EMPLID': cs_id})
    with mock(url):
        return http.request(url, auth=cs_api_auth())


def cs_api_auth():
    return HTTPBasicAuth(app.config['DEGREE_PROGRESS_API_USERNAME'], app.config['DEGREE_PROGRESS_API_PASSWORD'])
