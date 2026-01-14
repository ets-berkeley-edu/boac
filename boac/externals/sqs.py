"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

import json
import uuid

from flask import current_app as app

from boac.externals.aws import get_session

"""Client code to run SQS message operations."""


def send(table, operation, rows):
    queue_url = app.config['AWS_SQS_QUEUE_URL']
    if not queue_url:
        return

    client = _get_client()
    for row in rows:
        try:
            message_deduplication_id = str(uuid.uuid4())
            if table == 'note_topics':
                message_group_id = str(row['note_id'])
            else:
                message_group_id = str(row['id'])
            client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    'table': table,
                    'operation': operation,
                    'row': row,
                }),
                MessageGroupId=message_group_id,
                MessageDeduplicationId=message_deduplication_id,
            )
            app.logger.debug(
                f'SQS message sent (table={table}, operation={operation}, group_id={message_group_id}, deduplication_id={message_deduplication_id})',
            )

        except Exception as e:
            app.logger.exception(
                f'SQS send operation failed (table={table}, operation={operation}, '
                f'group_id={message_group_id}, deduplication_id={message_deduplication_id})',
                exc_info=e,
            )


def receive():
    queue_url = app.config['AWS_SQS_QUEUE_URL']
    if not queue_url:
        return None
    client = _get_client()
    return client.receive_message(QueueUrl=queue_url, AttributeNames=['All'], WaitTimeSeconds=1)


def _get_client():
    session = get_session()
    return session.client('sqs', region_name=app.config['AWS_REGION'])
