import requests

from flask import current_app as app

def request(url, headers):
    app.logger.debug({'message': 'HTTP request', 'url': url, 'headers': headers})
    try:
        # TODO handle methods other than GET
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        app.logger.error(e)
        return None
    else:
        return response
