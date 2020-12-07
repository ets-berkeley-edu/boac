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

import datetime
from datetime import timedelta
import os.path
import pickle

from flask import current_app as app
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_calendar_events():
    credentials = _get_credentials()
    if credentials:
        # Call the Calendar API
        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        now = (datetime.datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
        # Get the upcoming 10 events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime',
        ).execute()
        events = events_result.get('items', [])
        if not events:
            return []
        else:
            decorated = []
            for event in events:
                decorated.append(
                    {
                        'attendees': event.get('attendees', []),
                        'createdAt': event.get('created'),
                        'creator': event.get('creator'),
                        'end': event.get('end').get('dateTime'),
                        'hangoutLink': event.get('hangoutLink'),
                        'id': event.get('id'),
                        'link': event.get('htmlLink'),
                        'recurringEventId': event.get('recurringEventId'),
                        'start': event.get('start').get('dateTime'),
                        'status': event.get('status'),
                        'summary': event.get('summary'),
                        'updatedAt': event.get('updated'),
                    },
                )
            return decorated
    else:
        app.logger.warn('Unable to query Calendar API due to nil credentials.')
        return []


def _get_credentials():
    credentials = None
    base_dir = app.config['BASE_DIR']
    token_pickle_path = f'{base_dir}/config/token.pickle'
    if os.path.exists(token_pickle_path):
        # TODO: The real appointments feature will have a "token.pickle" per advisor, stored in db or similar.
        # The token.pickle file stores the user's access and refresh tokens, and is created automatically when the
        # authorization flow completes for the first time.
        with open(token_pickle_path, 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available we need user to grant access (OAuth).
    if not credentials or not credentials.valid:
        try:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                client_secrets_file = app.config['GOOGLE_CLIENT_SECRETS_JSON']
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file,
                    SCOPES,
                )
                credentials = flow.run_local_server()
            # TODO: Save the credentials in database?
            with open(token_pickle_path, 'wb') as token:
                pickle.dump(credentials, token)
        except Exception as e:
            app.logger.exception(e)
            app.logger.error('Failed to init or refresh Google credentials')

    return credentials
