import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Path to the token file on the persistent disk
TOKEN_FILE = "/data/token.json"

def load_credentials():
    """Load credentials from the JSON file."""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(f"Token file not found: {TOKEN_FILE}")
    with open(TOKEN_FILE, "r") as f:
        creds_info = json.load(f)
    return Credentials.from_authorized_user_info(creds_info)

def save_credentials(creds):
    """Save credentials to the JSON file."""
    creds_json = creds.to_json()
    with open(TOKEN_FILE, "w") as f:
        f.write(creds_json)

def get_authenticated_service():
    """Load credentials, refresh if expired, save after refresh, and return a service object."""
    creds = load_credentials()

    # If credentials are expired and have a refresh token, refresh them
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save the updated credentials back to the file
        save_credentials(creds)
        print("Token refreshed and saved.")

    # Build the Gmail service (or any other Google API)
    service = build('gmail', 'v1', credentials=creds)
    return service

def main():
    service = get_authenticated_service()

    # Example: List Gmail labels
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(f"- {label['name']}")

if __name__ == '__main__':
    main()