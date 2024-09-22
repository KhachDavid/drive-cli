import os
import argparse
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from File import File
from googleapiclient.errors import HttpError


# Scopes for accessing Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Global set to keep track of downloaded IDs
downloaded_ids = set()
default_folder_name = 'downloads_1'

def main():
    args = parse_args()
    service = authenticate_drive_api()

    if args.list:
        list_files(service)
    elif args.download:
        download_file(service, args.download[0], args.download[1])
    elif args.all:
        download_from_root(service)
    else:
        print("No valid arguments provided. Use --list, --download <id> <name>, or -d.")

def authenticate_drive_api():
    creds = None
    # Check if token.json exists to store the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials exist, let the user log in via the browser
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Here we initiate the InstalledAppFlow and open a local server for authentication
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Use the local server for authentication flow
        # Save the credentials for the next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build the Google Drive API service
    service = build('drive', 'v3', credentials=creds)
    return service


def list_files(service, page_size=10):
    # Call the Drive API to list the first 10 files
    results = service.files().list(
        pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    files = []

    if not items:
        print('No files found.')
    else:
        for item in items:
            new_file = File(name=item["name"],id=item["id"])
            files.append(new_file)

    return files

def download_file(service, file_id, parent_folder=default_folder_name):
    if file_id in downloaded_ids:
        return

    try:
        # Get the file's metadata
        metadata = service.files().get(fileId=file_id, fields='mimeType, name, parents').execute()
        mime_type = metadata.get('mimeType')
        file_name = metadata.get('name')

        # Check if it's a folder
        if mime_type == 'application/vnd.google-apps.folder':
            print(f"Entering folder: {file_name}")
            list_and_download_folder_contents(service, file_id, parent_folder)
            return
        
        # Handle Google Earth files
        elif mime_type == 'application/vnd.google-earth.kml+xml':
            request = service.files().get_media(fileId=file_id)
            file_name = f"{file_name}.kml"
        # Handle Google Forms
        elif mime_type == 'application/vnd.google-apps.form':
            request = service.files().export(fileId=file_id, mimeType='application/pdf')
            file_name = f"{file_name}.pdf"
        # Set the request and file extension based on the MIME type
        elif mime_type == 'application/vnd.google-apps.document':
            request = service.files().export(fileId=file_id, mimeType='application/pdf')
            file_name = f"{file_name}.pdf"
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            request = service.files().export(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            file_name = f"{file_name}.xlsx"
        elif mime_type == 'application/vnd.google-apps.presentation':
            request = service.files().export(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            file_name = f"{file_name}.pptx"
        else:
            request = service.files().get_media(fileId=file_id)

        # Create the directory structure
        file_path = os.path.join(parent_folder, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Download the file
        with open(file_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloaded {int(status.progress() * 100)}% for {file_name}.")
        print(f"File {file_name} downloaded to {file_path}.")
        
        # Mark this file ID as downloaded
        downloaded_ids.add(file_id)

    except HttpError as error:
        print(f"An error occurred: {error}")

def list_and_download_folder_contents(service, folder_id, parent_folder):
    # List files in the specified folder
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    if not items:
        print(f"No files found in folder: {parent_folder}.")
    else:
        for item in items:
            download_file(service, item['id'], parent_folder)

def download_from_root(service):
    # Start by listing the files in the root directory
    root_folder_id = 'root'
    list_and_download_folder_contents(service, root_folder_id, default_folder_name)

def download_file(service, file_id, file_name, parent_folder=default_folder_name):
    if file_id in downloaded_ids:
        print(f"Skipping already downloaded: {file_name}")
        return

    try:
        # Get the file's metadata to check its MIME type and parents
        metadata = service.files().get(fileId=file_id, fields='mimeType, name, parents').execute()
        mime_type = metadata.get('mimeType')
        parents = metadata.get('parents', [])
        file_name = metadata.get('name')

        # Check if it's a folder
        if mime_type == 'application/vnd.google-apps.folder':
            print(f"Entering folder: {file_name}")
            current_folder_path = os.path.join(parent_folder, file_name)
            list_and_download_folder_contents(service, file_id, current_folder_path)
            return

        # Set the request based on the MIME type
        if mime_type == 'application/vnd.google-apps.document':
            request = service.files().export(fileId=file_id, mimeType='application/pdf')
            file_name = f"{file_name}.pdf"
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            request = service.files().export(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            file_name = f"{file_name}.xlsx"
        elif mime_type == 'application/vnd.google-apps.presentation':
            request = service.files().export(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            file_name = f"{file_name}.pptx"
        else:
            request = service.files().get_media(fileId=file_id)

        # Create the directory structure
        file_path = os.path.join(parent_folder, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Download the file
        with open(file_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloaded {int(status.progress() * 100)}% for {file_name}.")
        print(f"File {file_name} downloaded to {file_path}.")
        
        # Mark this file ID as downloaded
        downloaded_ids.add(file_id)

    except HttpError as error:
        print(f"An error occurred: {error}")

def list_and_download_folder_contents(service, folder_id, parent_folder=default_folder_name):
    # List files in the specified folder
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    if not items:
        print(f"No files found in folder: {parent_folder}.")
    else:
        for item in items:
            download_file(service, item['id'], item['name'], parent_folder)

# Download all files in Google Drive
def download_all_files(service):
    results = service.files().list(fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        for item in items:
            print(f"Downloading {item['name']}...")
            download_file(service, item['id'], item['name'])

# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        prog='Google Drive CLI',
        description='CLI tool to interact with Google Drive. Supports file listing and downloading.',
        epilog='Use --list to list files, --download <id> <name> to download a file, or --all to download all files.')

    parser.add_argument('--list', action='store_true', help="List files in Google Drive.")
    parser.add_argument('--download', nargs=2, metavar=('id', 'name'), help="Download a file by its ID.")
    parser.add_argument('--all', action='store_true', help="Download all files from Google Drive.")
    return parser.parse_args()

if __name__ == "__main__":
    main()