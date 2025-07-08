import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

TOKEN_FILE = 'user_token.pickle'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_user_credentials():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
        if creds and creds.valid:
            return creds
        elif creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            return creds
    return None

def upload_to_drive(file_path, folder_id):
    creds = get_user_credentials()
    if not creds:
        raise Exception("User is not authorized. Please visit /authorize first.")

    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"[DRIVE] File uploaded successfully with ID: {file.get('id')}")
    return file.get('id')
