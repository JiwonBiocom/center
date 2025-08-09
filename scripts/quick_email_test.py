#!/usr/bin/env python3
"""빠른 이메일 테스트"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_notifier import EmailNotifier
from datetime import datetime

# 이메일 주소 입력
email = input("테스트 이메일을 받을 주소를 입력하세요: ").strip()
if not email:
    print("이메일 주소가 필요합니다!")
    exit(1)

# 발신자 이메일 설정
sender = input("발신자 이메일 주소를 입력하세요 (Gmail 계정): ").strip()
if sender:
    os.environ['GMAIL_SENDER_EMAIL'] = sender

# EmailNotifier 초기화
notifier = EmailNotifier()

# 테스트 이메일 발송
print(f"\n📧 {email}로 테스트 이메일을 발송합니다...")

success = notifier.send_email(
    [email],
    "🎉 AIBIO 이메일 알림 테스트 성공!",
    f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #4CAF50;">✅ Gmail 설정이 완료되었습니다!</h2>
        
        <p>AIBIO 시스템의 이메일 알림이 정상적으로 작동하고 있습니다.</p>
        
        <h3>설정된 알림:</h3>
        <ul>
            <li>🚨 Health Check 실패 알림</li>
            <li>📊 데이터베이스 스키마 변경 알림</li>
            <li>🎯 커스텀 시스템 알림</li>
        </ul>
        
        <p style="color: #666; font-size: 12px; margin-top: 30px;">
            발송 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            이 이메일은 AIBIO 시스템 자동 알림 테스트입니다.
        </p>
    </body>
    </html>
    """,
    is_html=True
)

if success:
    print("✅ 이메일이 성공적으로 발송되었습니다!")
    print("📬 받은편지함(또는 스팸함)을 확인해주세요.")
else:
    print("❌ 이메일 발송에 실패했습니다.")