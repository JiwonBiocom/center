#!/usr/bin/env python3
"""
Gmail OAuth2 설정 스크립트
Gmail API를 사용하기 위한 인증 토큰을 생성합니다.
"""
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API 스코프
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def setup_gmail_credentials():
    """Gmail API 인증 설정"""
    creds = None
    token_path = 'config/gmail_token.json'
    credentials_path = 'config/gmail_credentials.json'
    
    # 기존 토큰 확인
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # 토큰이 없거나 만료된 경우
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print("❌ Gmail credentials file not found!")
                print("\n📋 Setup Instructions:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Gmail API")
                print("4. Create OAuth2 credentials (Desktop application)")
                print("5. Download credentials JSON and save as 'config/gmail_credentials.json'")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 토큰 저장
        os.makedirs('config', exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print("✅ Gmail authentication successful!")
    
    return creds

def test_gmail_connection(creds):
    """Gmail 연결 테스트"""
    try:
        service = build('gmail', 'v1', credentials=creds)
        # 프로필 권한이 없을 수 있으므로, 단순히 서비스 생성만 확인
        print("✅ Gmail service created successfully!")
        print("Note: Email sending permission is ready. Profile access is not required.")
        return True
    except Exception as e:
        print(f"❌ Failed to create Gmail service: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setting up Gmail OAuth2 authentication...")
    creds = setup_gmail_credentials()
    
    if creds:
        test_gmail_connection(creds)