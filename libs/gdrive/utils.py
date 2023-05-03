from __future__ import print_function
from __future__ import print_function

import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from libs.gdrive.consts import EXAMPLE_FILE_ID, GDRIVE_SCOPES
from libs.gdrive.exceptions import NoGoogleDriveTokenFoundException

gdrive_service = None


def get_google_drive_service():
    global gdrive_service

    if gdrive_service is not None:
        return gdrive_service

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', GDRIVE_SCOPES)
    else:
        raise NoGoogleDriveTokenFoundException

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    gdrive_service = build('drive', 'v3', credentials=creds)
    return gdrive_service


def get_or_create_user_table(client_id: str):
    service = get_google_drive_service()

    result = service.files().list(
        q=f"name = '{client_id}.xlsx'",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    items = result.get('files', [])

    if not items:
        copy = service.files().copy(
            fileId=EXAMPLE_FILE_ID
        ).execute()
        service.files().update(
            fileId=copy.get("id"),
            body={'name': f'{client_id}.xlsx'}
        ).execute()
        permission = {
            'type': 'anyone',
            'value': 'anyone',
            'role': 'writer'
        }
        service.permissions().create(fileId=copy.get('id'), body=permission).execute()
        file = service.files().get(fileId=copy.get('id'), fields='webViewLink').execute()
