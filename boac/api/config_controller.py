import json
from boac.lib.http import tolerant_jsonify
from flask import current_app as app


@app.route('/api/config')
def app_config():
    return tolerant_jsonify({
        'boacEnv': app.config['BOAC_ENV'],
        'devAuthEnabled': app.config['DEVELOPER_AUTH_ENABLED'],
        'googleAnalyticsId': app.config['GOOGLE_ANALYTICS_ID'],
    })


@app.route('/api/version')
def app_version():
    v = {}
    metadata = load_json('bower.json')
    if metadata:
        v.update({
            'version': metadata['version'],
        })
    build_stats = load_json('config/build-summary.json')
    if build_stats:
        v.update(build_stats)
    else:
        v.update({
            'build': None,
        })
    return tolerant_jsonify(v)


def load_json(relative_path):
    try:
        file = open(app.config['BASE_DIR'] + '/' + relative_path)
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None
