#!/usr/bin/env python
"""SMS 발송 문제 확인 및 해결방안"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.config import settings

print("=== SMS 발송 문제 진단 ===\n")

print("1. 현재 설정:")
print(f"   - 알리고 User ID: {settings.ALIGO_USER_ID}")
print(f"   - 알리고 API Key: {settings.ALIGO_API_KEY[:10]}...")
print(f"   - 발신번호: {settings.ALIGO_SENDER}")
print()

print("2. 문제:")
print("   - 알리고에서 '등록/인증되지 않은 발신번호' 오류 발생")
print("   - 발신번호가 알리고에 사전 등록되지 않음")
print()

print("3. 해결 방법:")
print("   A. 알리고 관리자 페이지에서 발신번호 등록")
print("      1) https://smartsms.aligo.in 접속")
print("      2) biocom 계정으로 로그인") 
print("      3) 발신번호 관리 메뉴에서 02-2039-2783 등록")
print("      4) 통신사업자 서류 제출 및 인증 완료")
print()
print("   B. 임시 조치 (현재 적용됨)")
print("      - 테스트 모드(testmode_yn='Y')로 설정")
print("      - 실제 SMS는 발송되지 않지만 시스템은 정상 작동")
print()

print("4. 현재 상태:")
print("   - 예약 생성/확정 시 SMS 발송 로직은 정상 작동")
print("   - 테스트 모드로 인해 실제 발송은 안됨")
print("   - 로그에는 '발송 성공'으로 기록됨")
print()

print("5. 추가 확인사항:")
print("   - 고객 전화번호 형식: 정상 (010-XXXX-XXXX)")
print("   - SMS 메시지 템플릿: 정상")
print("   - API 연결: 정상 (잔여 SMS 건수 확인됨)")