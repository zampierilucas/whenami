# Copyright 2025 Lucas Zampieri
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes needed for the application
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events.readonly',
    'https://www.googleapis.com/auth/calendar.freebusy'
]


def get_config_dir():
    """Get the config directory path and create it if it doesn't exist"""
    config_dir = Path.home() / '.config' / 'whenami'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def authenticate_google_calendar():
    """Authenticate and return Google Calendar service with proper error handling"""
    try:
        config_dir = get_config_dir()
        token_path = config_dir / 'token.json'
        credentials_path = config_dir / 'credentials.json'
        
        # Check for token in config directory first, then fallback to current directory
        creds = None
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            except Exception as e:
                print(f"[WARNING] Error loading existing token from {token_path}: {e}")
                token_path.unlink()
        elif os.path.exists('token.json'):
            try:
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            except Exception as e:
                print(f"[WARNING] Error loading existing token: {e}")
                os.remove('token.json')

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"[WARNING] Error refreshing token: {e}")
                    creds = None

            if not creds:
                # Check for credentials.json in config directory first, then fallback to current directory
                if credentials_path.exists():
                    credentials_file = str(credentials_path)
                elif os.path.exists('credentials.json'):
                    credentials_file = 'credentials.json'
                else:
                    print("[ERROR] credentials.json not found!")
                    print(f"Please place your credentials.json file in {credentials_path}")
                    print("Or follow the authentication setup in the README: https://github.com/zampierilucas/whenami#authentication")
                    sys.exit(1)

                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                # Custom authorization URL display
                flow._authorization_prompt_message = '\033]8;;{url}\033\\Click here to authorize\033]8;;\033\\ or visit: {url}'
                creds = flow.run_local_server(port=0, authorization_prompt_message='Please authorize this application by \033]8;;{url}\033\\clicking here\033]8;;\033\\')

            # Save token to config directory
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)

        # Test the connection
        try:
            service.calendarList().list().execute()
            return service
        except HttpError as e:
            print(f"[ERROR] Failed to access calendar: {e.reason}")
            if e.status_code == 403:
                print("Make sure you've enabled the Google Calendar API in your Google Cloud Console")
            sys.exit(1)

    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        print("Try removing token.json and running again")
        sys.exit(1)
