"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

import boto3
from flask import current_app as app
import smart_open


"""Client code to run file operations against S3."""


def build_s3_url(bucket, key, credentials=True):
    if credentials:
        credentials = ':'.join([app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_ACCESS_KEY']])
        return f's3://{credentials}@{bucket}/{key}'
    else:
        return f's3://{bucket}/{key}'


def stream_object(bucket, key):
    s3_url = build_s3_url(bucket, key)
    try:
        return smart_open.open(s3_url, 'rb')
    except Exception as e:
        app.logger.error(f'S3 stream operation failed (bucket={bucket}, key={key})')
        app.logger.exception(e)
        return None


def put_file_to_s3(bucket, key, path_to_file):
    put_binary_data_to_s3(bucket=bucket, key=key, binary_data=open(path_to_file, 'rb'))


def put_binary_data_to_s3(bucket, key, binary_data):
    _get_client().put_object(Body=binary_data, Bucket=bucket, Key=key, ServerSideEncryption='AES256')


def _get_client():
    return boto3.client(
        's3',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=app.config['DATA_LOCH_S3_REGION'],
    )
