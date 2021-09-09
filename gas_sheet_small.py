#!/usr/bin/env python
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Sheet:
    creds = None
    sheet_name = ''
    service = None
    spreadsheet_id = None

    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.pickle')
        credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.json')

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, ['https://www.googleapis.com/auth/spreadsheets'])
                self.creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('sheets', 'v4', credentials=self.creds)

    def select_sheet(self, name):
        if name is not None:
            self.sheet_name = f'{name}!'
        else:
            self.sheet_name = ''

    def get(self, range_):
        request = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=f'{self.sheet_name}{range_}', valueRenderOption='FORMATTED_VALUE')
        response = request.execute()
        return response['values']

    def set_(self, range_, table):
        body = {
            'range': f'{self.sheet_name}{range_}',
            'majorDimension': 'ROWS',
            'values': table
        }
        request = self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, valueInputOption='USER_ENTERED', range=f'{self.sheet_name}{range_}', body=body)
        response = request.execute()
        return response
      
