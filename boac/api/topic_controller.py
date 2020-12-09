"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""
from boac.api.errors import BadRequestError
from boac.api.util import admin_required, advising_data_access_required, scheduler_required
from boac.lib.http import tolerant_jsonify
from boac.lib.util import to_bool_or_none
from boac.models.topic import Topic
from flask import current_app as app, request


@app.route('/api/topics/all')
@advising_data_access_required
def get_all_topics():
    include_deleted = to_bool_or_none(request.args.get('includeDeleted'))
    topics = Topic.get_all(include_deleted=include_deleted)
    return tolerant_jsonify(_to_sorted_json(topics))


@app.route('/api/topics/for_appointments')
@scheduler_required
def get_topics_for_appointment():
    include_deleted = to_bool_or_none(request.args.get('includeDeleted'))
    topics = Topic.get_all(available_in_appointments=True, include_deleted=include_deleted)
    return tolerant_jsonify(_to_sorted_json(topics))


@app.route('/api/topics/for_notes')
@advising_data_access_required
def get_topics_for_notes():
    include_deleted = to_bool_or_none(request.args.get('includeDeleted'))
    topics = Topic.get_all(available_in_notes=True, include_deleted=include_deleted)
    return tolerant_jsonify(_to_sorted_json(topics))


@app.route('/api/topic/create', methods=['POST'])
@admin_required
def create_topic():
    params = request.json
    topic = params.get('topic', '').strip()
    available_in_notes = to_bool_or_none(params.get('availableInNotes')) or False
    available_in_appointments = to_bool_or_none(params.get('availableInAppointments')) or False
    if not topic or not (available_in_notes or available_in_appointments):
        raise BadRequestError('Required parameters are missing.')
    topic = Topic.create_topic(
        topic,
        available_in_notes=available_in_notes,
        available_in_appointments=available_in_appointments,
    )
    return tolerant_jsonify(topic.to_api_json())


@app.route('/api/topic/update', methods=['POST'])
@admin_required
def update_topic():
    params = request.json
    topic_id = params.get('id')
    topic = params.get('topic', '').strip()
    available_in_notes = to_bool_or_none(params.get('availableInNotes')) or False
    available_in_appointments = to_bool_or_none(params.get('availableInAppointments')) or False
    if not topic_id or not topic or not (available_in_notes or available_in_appointments):
        raise BadRequestError('Required parameters are missing.')
    topic = Topic.update_topic(
        topic_id=topic_id,
        topic=topic,
        available_in_notes=available_in_notes,
        available_in_appointments=available_in_appointments,
    )
    return tolerant_jsonify(topic.to_api_json())


@app.route('/api/topic/delete/<topic_id>', methods=['DELETE'])
@admin_required
def delete_topic(topic_id):
    Topic.delete(topic_id=topic_id)
    return tolerant_jsonify({'message': f'Topic {topic_id} deleted'}), 200


@app.route('/api/topic/undelete', methods=['POST'])
@admin_required
def undelete_topic():
    params = request.json
    topic_id = params.get('id')
    Topic.undelete(topic_id=topic_id)
    return tolerant_jsonify(Topic.find_by_id(topic_id).to_api_json())


@app.route('/api/topics/usage_statistics')
@admin_required
def usage_statistics():
    return tolerant_jsonify(Topic.get_usage_statistics())


def _to_sorted_json(topics):
    indices_of_other = [index for index, topic in enumerate(topics) if topic.topic.startswith('Other')]
    for index in indices_of_other:
        topics.append(topics.pop(index))
    return [topic.to_api_json() for topic in topics]
