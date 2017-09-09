import requests

from flask import current_app as app

def request(url, headers):
    app.logger.debug({'message': 'HTTP request', 'url': url, 'headers': sanitize_headers(headers)})
    try:
        # TODO handle methods other than GET
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        app.logger.error(e)
    return response

def sanitize_headers(headers):
    '''Suppress authorization token in logged headers.'''
    if headers['Authorization']:
        sanitized = headers.copy()
        sanitized['Authorization'] = 'Bearer <token>'
        return sanitized
    else:
        return headers
