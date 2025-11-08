"""
Gmail API service for sending emails
"""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path

# If modifying these scopes, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Get authenticated Gmail API service"""
    creds = None
    token_path = Path(__file__).parent.parent / 'token.json'
    credentials_path = Path(__file__).parent.parent.parent / 'credentials.json'
    
    # Token file stores the user's access and refresh tokens
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                raise Exception("Gmail API token expired. Please run authorize_gmail.py to re-authenticate.")
        else:
            raise Exception(
                f"Gmail API not authorized. credentials.json found at {credentials_path}, "
                "but token.json is missing. Please run authorize_gmail.py to authenticate."
            )
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, text_content, html_content):
    """Create a message for an email"""
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Attach both plain text and HTML versions
    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    
    message.attach(part1)
    message.attach(part2)
    
    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_email_via_gmail_api(to_email, subject, text_content, html_content):
    """Send email using Gmail API"""
    try:
        service = get_gmail_service()
        sender_email = "luisaccforwork@gmail.com"  # Your Gmail address
        
        message = create_message(
            sender_email,
            to_email,
            subject,
            text_content,
            html_content
        )
        
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        return {
            'success': True,
            'message_id': sent_message['id']
        }
    
    except Exception as e:
        print(f"Error sending email via Gmail API: {e}")
        return {
            'success': False,
            'error': str(e)
        }
