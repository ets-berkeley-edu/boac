"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

from contextlib import contextmanager

import boto3
import moto


@contextmanager
def mock_eop_note_attachment(app):
    with moto.mock_s3():
        bucket = app.config['DATA_LOCH_S3_EOP_ADVISING_NOTE_BUCKET']
        s3 = boto3.resource('s3', app.config['DATA_LOCH_S3_REGION'])
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': app.config['DATA_LOCH_S3_REGION']})
        key = f"{app.config['DATA_LOCH_S3_EOP_NOTE_ATTACHMENTS_PATH']}/eop_advising_note_101_i am attached.txt"
        s3.Object(bucket, key).put(Body="A wizard's job is to vex chumps quickly in fog.")
        yield s3


@contextmanager
def mock_legacy_appointment_attachment(app):
    with moto.mock_s3():
        bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
        s3 = boto3.resource('s3', app.config['DATA_LOCH_S3_REGION'])
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': app.config['DATA_LOCH_S3_REGION']})
        key = f"{app.config['DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH']}/9100000000/9100000000_00010_1.pdf"
        s3.Object(bucket, key).put(Body='01001000 01100101 01101100 01101100 01101111 00100000 01010111 01101111 01110010 01101100 01100100')
        yield s3


@contextmanager
def mock_sis_note_attachment(app):
    with moto.mock_s3():
        bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
        s3 = boto3.resource('s3', app.config['DATA_LOCH_S3_REGION'])
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': app.config['DATA_LOCH_S3_REGION']})
        key = f"{app.config['DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH']}/9000000000/9000000000_00002_1.pdf"
        s3.Object(bucket, key).put(Body='When in the course of human events, it becomes necessarf arf woof woof woof')
        yield s3


@contextmanager
def mock_advising_note_s3_bucket(app):
    with moto.mock_s3():
        bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
        s3 = boto3.resource('s3', app.config['DATA_LOCH_S3_REGION'])
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': app.config['DATA_LOCH_S3_REGION']})
        yield s3


@contextmanager
def override_config(app, key, value):
    """Temporarily override an app config value."""
    old_value = app.config[key]
    app.config[key] = value
    try:
        yield
    finally:
        app.config[key] = old_value


@contextmanager
def pause_mock_sts():
    """Temporarily pause moto's mock STS, which can get in the way of tests incorporating other external services, such as CAS."""
    moto.mock_sts().stop()
    try:
        yield
    finally:
        moto.mock_sts().start()
