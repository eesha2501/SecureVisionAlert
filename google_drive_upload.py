import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_user_drive_service():
    creds = None
    if os.path.exists('user_token.pickle'):
        with open('user_token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('user_token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        else:
            raise Exception('User not authenticated. Please visit /authorize first.')

    service = build('drive', 'v3', credentials=creds)
    return service

def upload_to_drive(file_path, folder_id):
    service = get_user_drive_service()
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
