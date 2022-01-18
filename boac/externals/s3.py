"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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


def build_s3_url(bucket, key):
    return f's3://{bucket}/{key}'


def get_signed_urls(bucket, keys, expiration):
    client = _get_client()
    return {key: _get_signed_url(client, bucket, key, expiration) for key in keys}


def stream_object(bucket, key):
    s3_url = build_s3_url(bucket, key)
    session = _get_session()
    try:
        return smart_open.open(s3_url, 'rb', transport_params=dict(session=session))
    except Exception as e:
        app.logger.error(f'S3 stream operation failed (bucket={bucket}, key={key})')
        app.logger.exception(e)
        return None


def put_file_to_s3(bucket, key, path_to_file):
    put_binary_data_to_s3(bucket=bucket, key=key, binary_data=open(path_to_file, 'rb'))


def put_binary_data_to_s3(bucket, key, binary_data):
    _get_client().put_object(Body=binary_data, Bucket=bucket, Key=key, ServerSideEncryption=app.config['DATA_LOCH_S3_ENCRYPTION'])


def _get_sts_credentials():
    sts_client = boto3.client('sts')
    role_arn = app.config['AWS_APP_ROLE_ARN']
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='AssumeAppRoleSession',
        DurationSeconds=900,
    )
    return assumed_role_object['Credentials']


def _get_session():
    credentials = _get_sts_credentials()
    return boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )


def _get_client():
    session = _get_session()
    return session.client('s3', region_name=app.config['DATA_LOCH_S3_REGION'])


def _get_signed_url(client, bucket, key, expiration):
    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key,
        },
        ExpiresIn=expiration,
    )
