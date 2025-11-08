#!/usr/bin/env python3
"""
Manual OAuth flow for headless servers
This will give you a URL to visit in browser and paste the auth code back
"""
import json
from pathlib import Path

def manual_oauth_flow():
    """Run OAuth flow manually for headless servers"""
    credentials_path = Path('credentials.json')
    
    if not credentials_path.exists():
        print("Error: credentials.json not found!")
        return
    
    with open(credentials_path) as f:
        creds_data = json.load(f)
    
    client_id = creds_data['installed']['client_id']
    client_secret = creds_data['installed']['client_secret']
    
    # OAuth URLs
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = "http://localhost"
    scope = "https://www.googleapis.com/auth/gmail.send"
    
    # Step 1: Generate authorization URL
    auth_link = (
        f"{auth_url}?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    print("=" * 80)
    print("Gmail API Manual Authorization")
    print("=" * 80)
    print("\n1. Visit this URL in your browser:\n")
    print(auth_link)
    print("\n2. Authorize the application")
    print("3. You will be redirected to localhost with a code in the URL")
    print("4. Copy the 'code' parameter from the URL")
    print("   Example: http://localhost/?code=YOUR_CODE_HERE&scope=...")
    print("\n" + "=" * 80)
    
    # Step 2: Get authorization code from user
    auth_code = input("\nPaste the authorization code here: ").strip()
    
    if not auth_code:
        print("Error: No code provided")
        return
    
    # Step 3: Exchange code for tokens
    import requests
    
    token_data = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    print("\nExchanging code for access token...")
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        tokens = response.json()
        
        # Save token in the format expected by google-auth
        token_info = {
            "token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "token_uri": token_url,
            "client_id": client_id,
            "client_secret": client_secret,
            "scopes": [scope]
        }
        
        token_path = Path('backend/token.json')
        with open(token_path, 'w') as f:
            json.dump(token_info, f, indent=2)
        
        print(f"\n✓ Success! Token saved to {token_path}")
        print("✓ You can now use Gmail API to send emails")
        
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    manual_oauth_flow()
