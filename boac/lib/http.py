import urllib

from flask import current_app as app
from flask import Response
import requests
import simplejson as json


class ResponseExceptionWrapper:
    def __init__(self, exception, original_response=None):
        self.exception = exception
        self.raw_response = original_response

    def __bool__(self):
        return False


def build_url(url, query=None):
    encoded_query = urllib.parse.urlencode(query, doseq=True) if query else ''
    url_components = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse([
        url_components.scheme,
        url_components.netloc,
        urllib.parse.quote(url_components.path),
        '',
        encoded_query,
        '',
    ])


def get_next_page(response):
    if response.links and 'next' in response.links:
        return response.links['next'].get('url')
    else:
        return None


def request(url, headers={}, auth=None):
    """Exception and error catching wrapper for outgoing HTTP requests.

    :param url:
    :param headers:
    :return: The HTTP response from the external server, if the request was successful.
        Otherwise, a wrapper containing the exception and the original HTTP response, if
        one was returned.
        Borrowing the Requests convention, successful responses are truthy and failures are falsey.
    """
    app.logger.debug({'message': 'HTTP request', 'url': url, 'headers': sanitize_headers(headers)})
    response = None
    try:
        # TODO handle methods other than GET
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        app.logger.error(e)
        return ResponseExceptionWrapper(e, response)
    else:
        return response


def sanitize_headers(headers):
    """Suppress authorization token in logged headers."""
    if 'Authorization' in headers:
        # Canvas style.
        sanitized = headers.copy()
        sanitized['Authorization'] = 'Bearer <token>'
        return sanitized
    elif 'app_id' in headers:
        # Hub style.
        sanitized = headers.copy()
        sanitized['app_id'] = '<app_id>'
        sanitized['app_key'] = '<app_key>'
        return sanitized
    else:
        return headers


def tolerant_jsonify(obj, **kwargs):
    return Response(json.dumps(obj, ignore_nan=True, separators=(',', ':'), **kwargs), mimetype='application/json')
