import os
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/drive"]

def upload_basic():

    try:

        creds = None

        if os.path.exists("token-drive.json"):
            creds = Credentials.from_authorized_user_file("token-drive.json", SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("drive-file-upload.json", SCOPES)
                creds = flow.run_local_server(port=0)
                
            with open('token-drive.json', 'w') as token:
                token.write(creds.to_json())
        # create drive api client
        service = build("drive", "v3", credentials=creds)
        
        response = service.files().list(
            q="name='VCEC-FILE-STORAGE-BUCKET' and mimeType='application/vnd.google-apps.folder'"
        ).execute()
        
        if not response['files']:
            file_metadata={
                'name': 'VCEC-FILE-STORAGE-BUCKET',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            file = service.files().create(body=file_metadata, fields='id').execute()    

            print(f'File ID: {file.get("id")}')
            
        else:
            print(f'File ID: {response["files"][0].get("id")}')
            
            

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None



if __name__ == "__main__":
  upload_basic()