# gmail_api.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail_account():
    """Authenticate and return Gmail service."""
    creds = None
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pkl', 'wb') as token:
            pickle.dump(creds, token)
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def fetch_emails(service):
    """Fetch emails from Gmail."""
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])

        if not messages:
            print('No new messages.')
            return []

        email_data = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_info = {
                'subject': '',
                'body': '',
                'received_date': None,
                'from': '',
            }

            for header in msg['payload']['headers']:
                if header['name'] == 'Subject':
                    email_info['subject'] = header['value']
                if header['name'] == 'From':
                    email_info['from'] = header['value']
            
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        email_info['body'] = part['body']['data']
            
            email_info['received_date'] = datetime.fromtimestamp(int(msg['internalDate']) / 1000)

            email_data.append(email_info)

        return email_data
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []
