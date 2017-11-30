import json
from flask import current_app as app, jsonify


@app.route('/api/config')
def app_config():
    return jsonify({
        'boacEnv': app.config['BOAC_ENV'],
        'devAuthEnabled': app.config['DEVELOPER_AUTH_ENABLED'],
        'googleAnalyticsId': app.config['GOOGLE_ANALYTICS_ID'],
        'version': _get_app_version(),
    })


def _get_app_version():
    try:
        file = open(app.config['BASE_DIR'] + '/bower.json')
        return json.load(file)['version']
    except (FileNotFoundError, KeyError, TypeError):
        return None
