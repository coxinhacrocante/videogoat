from __future__ import print_function
from dataclasses import fields

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
#SCOPES = ['https://www.googleapis.com/auth/drive']

class Drive:
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        self.pasta = '1IJI-3-P4n4U5ZOGEqGj6WcKI8pMiVByoFWg5ZIyP94s'
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token_drive.json'):
            creds = Credentials.from_authorized_user_file('token_drive.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credenciais.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token_drive.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        # Call the Sheets API
        

    def postar(self, nome, arquivo, tipo):
        file_metadata = {'name': nome}
        media = MediaFileUpload(arquivo,
                        mimetype=tipo)
        file = self.service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
        return file.get('id')

    def gerar_link(self, file_id):

        requerir = {
            'type': 'anyone',
            'role': 'reader'}

        self.service.permissions().create(
                fileId=file_id,
                body=requerir
        ).execute()

        link = self.service.files().get(
            fileId = file_id,
            fields = 'webViewLink'
        ).execute()

        return link