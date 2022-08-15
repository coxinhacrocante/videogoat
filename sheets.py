from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
#SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
#SPREADSHEET_ID = '1IJI-3-P4n4U5ZOGEqGj6WcKI8pMiVByoFWg5ZIyP94s'

class Sheets:
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SPREADSHEET_ID = '1IJI-3-P4n4U5ZOGEqGj6WcKI8pMiVByoFWg5ZIyP94s'
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credenciais.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        self.sheet = service.spreadsheets()
    
    def receber(self, RANGE):
        resultado = self.sheet.values().get(spreadsheetId=self.SPREADSHEET_ID,
            range=RANGE).execute()
        valores = resultado.get('values', [])
        return valores
    
    def modificar(self, RANGE, conteudo):
        resultado = self.sheet.values().update(spreadsheetId=self.SPREADSHEET_ID,
            range=RANGE,
            valueInputOption = 'USER_ENTERED',
            body={'values':conteudo}).execute()
