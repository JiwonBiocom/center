#!/usr/bin/env python
"""알리고 발신번호 테스트"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from services.aligo_service import aligo_service
from core.config import settings
import requests

def check_sender_number():
    """발신번호 확인 및 테스트"""
    print("=== 알리고 SMS 설정 확인 ===")
    print(f"User ID: {settings.ALIGO_USER_ID}")
    print(f"API Key: {settings.ALIGO_API_KEY[:10]}...")
    print(f"Sender: {settings.ALIGO_SENDER}")
    print()
    
    # 잔여 건수 조회로 API 연결 테스트
    print("1. API 연결 테스트 (잔여 건수 조회):")
    result = aligo_service.get_remain_sms()
    print(f"   결과: {result}")
    print()
    
    # 발신번호 리스트 조회
    print("2. 등록된 발신번호 조회:")
    try:
        data = {
            "key": settings.ALIGO_API_KEY,
            "user_id": settings.ALIGO_USER_ID
        }
        
        response = requests.post(
            "https://apis.aligo.in/sender_list/",
            data=data,
            timeout=10
        )
        
        result = response.json()
        print(f"   응답: {result}")
        
        if result.get("result_code") == "1" and result.get("list"):
            print("\n   등록된 발신번호:")
            for sender in result.get("list", []):
                print(f"   - {sender.get('sender', 'N/A')} ({sender.get('status', 'N/A')})")
        
    except Exception as e:
        print(f"   오류: {e}")
    
    print()
    
    # 테스트 SMS 발송
    print("3. 테스트 SMS 발송 (테스트모드):")
    test_result = aligo_service.send_sms(
        receiver="01012345678",  # 테스트 번호
        message="테스트 메시지",
        testmode_yn="Y"  # 테스트 모드로 실제 발송 안함
    )
    print(f"   결과: {test_result}")

if __name__ == "__main__":
    check_sender_number()