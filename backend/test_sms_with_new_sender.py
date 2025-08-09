#!/usr/bin/env python
"""변경된 발신번호로 SMS 테스트"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from services.aligo_service import aligo_service
from core.config import settings

def test_sms():
    print("=== SMS 발송 테스트 ===")
    print(f"발신번호: {settings.ALIGO_SENDER}")
    print()
    
    # 실제 발송 테스트
    result = aligo_service.send_sms(
        receiver="010-3934-8641",  # 전태준 고객 번호
        message="[AIBIO 센터] 테스트 메시지입니다.\n\n발신번호 변경 후 테스트 발송입니다.\n\n문의: 02-2039-2783"
    )
    
    print(f"발송 결과: {result}")
    
    if result["success"]:
        print("\n✅ SMS 발송 성공!")
        print(f"   - 메시지 ID: {result.get('message_id')}")
        print(f"   - 메시지 타입: {result.get('msg_type')}")
    else:
        print("\n❌ SMS 발송 실패!")
        print(f"   - 오류 코드: {result.get('error_code')}")
        print(f"   - 오류 메시지: {result.get('error_message')}")

if __name__ == "__main__":
    test_sms()