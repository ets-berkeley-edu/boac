from flask import current_app as app
import requests


class ResponseExceptionWrapper:
    def __init__(self, exception, original_response = None):
        self.exception = exception
        self.raw_response = original_response
    def __bool__(self):
        return False

def request(url, headers):
    """
    Exception and error catching wrapper for outgoing HTTP requests.
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
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        app.logger.error(e)
        return ResponseExceptionWrapper(e, response)
    else:
        return response


def sanitize_headers(headers):
    """Suppress authorization token in logged headers."""
    if headers['Authorization']:
        sanitized = headers.copy()
        sanitized['Authorization'] = 'Bearer <token>'
        return sanitized
    else:
        return headers
