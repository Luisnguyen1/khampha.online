#!/usr/bin/env python3
"""
Script to authorize Gmail API and generate token.json
Run this on your local machine or server with browser access
"""
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authorize_gmail():
    """Authorize Gmail API and save credentials"""
    creds = None
    token_path = Path(__file__).parent / 'backend' / 'token.json'
    credentials_path = Path(__file__).parent / 'credentials.json'
    
    # Check if credentials.json exists
    if not credentials_path.exists():
        print(f"Error: credentials.json not found at {credentials_path}")
        print("Please download it from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to APIs & Services > Credentials")
        print("4. Download OAuth 2.0 Client ID credentials")
        return False
    
    # Token file stores the user's access and refresh tokens
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth flow...")
            print("A browser window will open for you to authorize the application.")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for the next run
        print(f"Saving credentials to {token_path}")
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("✓ Authorization successful!")
        print(f"✓ Token saved to {token_path}")
        return True
    else:
        print("✓ Existing valid credentials found!")
        return True

if __name__ == '__main__':
    print("=" * 60)
    print("Gmail API Authorization")
    print("=" * 60)
    authorize_gmail()
