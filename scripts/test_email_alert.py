#!/usr/bin/env python3
"""
이메일 알림 테스트 스크립트
Gmail 설정이 올바르게 되어있는지 확인합니다.
"""
import os
import sys
from datetime import datetime

# 스크립트 경로를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_notifier import EmailNotifier

def test_email_notifications():
    """이메일 알림 테스트"""
    
    # 1. Gmail 설정 확인
    if not os.path.exists('config/gmail_token.json'):
        print("❌ Gmail not configured!")
        print("Run: python scripts/setup_gmail_oauth.py")
        return
    
    # 2. 수신자 설정
    recipients = input("테스트 이메일을 받을 주소를 입력하세요 (콤마로 구분): ").strip()
    if not recipients:
        print("❌ No recipients provided")
        return
    
    recipient_list = [email.strip() for email in recipients.split(',')]
    
    # 3. EmailNotifier 초기화
    notifier = EmailNotifier()
    
    print(f"\n📧 Sending test emails to: {recipient_list}")
    
    # 4. Health Check 알림 테스트
    print("\n1️⃣ Testing Health Check Alert...")
    test_health_report = {
        'timestamp': datetime.now().isoformat(),
        'database_healthy': False,
        'api_healthy': True,
        'overall_status': 'unhealthy'
    }
    
    success = notifier.send_health_check_alert(recipient_list, test_health_report)
    if success:
        print("✅ Health check alert sent successfully!")
    else:
        print("❌ Failed to send health check alert")
    
    # 5. 스키마 변경 알림 테스트
    print("\n2️⃣ Testing Schema Drift Alert...")
    test_schema_report = """## 🔍 Schema Drift Report

Generated at: 2025-06-21T12:00:00

### ➕ Added Tables
- `new_feature_table`

### 📝 Modified Tables

#### `customers`
- Added columns: `last_login`, `preferences`
- Removed columns: `old_field`

이 변경사항은 자동으로 감지되었으며, PR이 생성되었습니다."""
    
    success = notifier.send_schema_drift_alert(recipient_list, test_schema_report)
    if success:
        print("✅ Schema drift alert sent successfully!")
    else:
        print("❌ Failed to send schema drift alert")
    
    # 6. 일반 이메일 테스트
    print("\n3️⃣ Testing Custom Email...")
    success = notifier.send_email(
        recipient_list,
        "🎉 AIBIO 이메일 알림 테스트",
        """
        <h2>안녕하세요!</h2>
        <p>AIBIO 시스템의 이메일 알림이 정상적으로 작동하고 있습니다.</p>
        <ul>
            <li>Health Check 알림 ✅</li>
            <li>스키마 변경 알림 ✅</li>
            <li>커스텀 알림 ✅</li>
        </ul>
        <p>문제가 있으면 시스템 관리자에게 문의하세요.</p>
        """,
        is_html=True
    )
    
    if success:
        print("✅ Custom email sent successfully!")
    else:
        print("❌ Failed to send custom email")
    
    print("\n✨ Email test completed! Check your inbox (and spam folder).")

if __name__ == "__main__":
    print("🧪 AIBIO Email Notification Test")
    print("=" * 50)
    test_email_notifications()