from boac.lib.http import tolerant_jsonify
from boac.models.alert import Alert
from flask import current_app as app
from flask_login import current_user, login_required


@app.route('/api/alerts/current')
@login_required
def get_current_alerts():
    alerts = Alert.current_alerts(viewer_id=current_user.id)
    return tolerant_jsonify(alerts)


@app.route('/api/alerts/current/<sid>')
@login_required
def get_current_alerts_for_sid(sid):
    alerts = Alert.current_alerts_for_sid(viewer_id=current_user.id, sid=sid)
    return tolerant_jsonify(alerts)


@app.route('/api/alerts/<alert_id>/dismiss')
@login_required
def dismiss_alert(alert_id):
    current_user.dismiss_alert(alert_id)
    return tolerant_jsonify({'message': f'Alert {alert_id} dismissed by UID {current_user.uid}'}), 200
