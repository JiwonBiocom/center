"""
유입고객 관리 API 테스트 스크립트
"""
import requests
import json
from datetime import date, datetime
from typing import Dict, Any

# API 베이스 URL
BASE_URL = "http://localhost:8000/api/v1"

# 테스트용 토큰 (실제 환경에서는 로그인 후 받은 토큰 사용)
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN_HERE"
}

def print_response(response: requests.Response, title: str):
    """응답 출력 헬퍼"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")

def test_authentication():
    """인증 테스트 및 토큰 획득"""
    print("\n1. 인증 테스트")
    
    # 로그인
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers["Authorization"] = f"Bearer {token}"
        print("✅ 로그인 성공!")
        return True
    else:
        print("❌ 로그인 실패!")
        print(response.text)
        return False

def test_get_customer_leads():
    """유입고객 목록 조회 테스트"""
    print("\n2. 유입고객 목록 조회 테스트")
    
    # 기본 조회
    response = requests.get(f"{BASE_URL}/customer-leads/", headers=headers)
    print_response(response, "기본 목록 조회")
    
    # 필터링 테스트
    params = {
        "status": ["new", "phone_consulted"],
        "page_size": 10,
        "sort_by": "created_at",
        "sort_order": "desc"
    }
    response = requests.get(f"{BASE_URL}/customer-leads/", params=params, headers=headers)
    print_response(response, "필터링된 목록 조회")

def test_get_statistics():
    """통계 조회 테스트"""
    print("\n3. 통계 조회 테스트")
    
    response = requests.get(f"{BASE_URL}/customer-leads/stats", headers=headers)
    print_response(response, "유입고객 통계")

def test_create_customer_lead():
    """유입고객 생성 테스트"""
    print("\n4. 유입고객 생성 테스트")
    
    new_lead = {
        "name": "테스트 고객",
        "phone": "010-1234-5678",
        "lead_date": str(date.today()),
        "age": 35,
        "region": "서울",
        "lead_channel": "인스타그램",
        "db_channel": "구글폼",
        "price_informed": True,
        "notes": "API 테스트로 생성된 고객"
    }
    
    response = requests.post(f"{BASE_URL}/customer-leads/", json=new_lead, headers=headers)
    print_response(response, "유입고객 생성")
    
    if response.status_code == 200:
        return response.json()["lead_id"]
    return None

def test_get_customer_lead_detail(lead_id: int):
    """유입고객 상세 조회 테스트"""
    print("\n5. 유입고객 상세 조회 테스트")
    
    response = requests.get(f"{BASE_URL}/customer-leads/{lead_id}", headers=headers)
    print_response(response, "유입고객 상세 정보")

def test_update_customer_lead(lead_id: int):
    """유입고객 수정 테스트"""
    print("\n6. 유입고객 수정 테스트")
    
    update_data = {
        "phone_consult_date": str(date.today()),
        "phone_consult_result": "관심있음",
        "status": "phone_consulted",
        "notes": "전화 상담 완료. 다음주 방문 예정"
    }
    
    response = requests.put(f"{BASE_URL}/customer-leads/{lead_id}", json=update_data, headers=headers)
    print_response(response, "유입고객 정보 수정")

def test_add_consultation_history(lead_id: int):
    """상담 이력 추가 테스트"""
    print("\n7. 상담 이력 추가 테스트")
    
    consultation = {
        "lead_id": lead_id,
        "consultation_type": "phone",
        "consultation_date": datetime.now().isoformat(),
        "result": "관심있음",
        "notes": "가격 문의. 패키지 설명 완료",
        "next_action": "방문 상담 예약"
    }
    
    response = requests.post(f"{BASE_URL}/customer-leads/{lead_id}/consultations", json=consultation, headers=headers)
    print_response(response, "상담 이력 추가")

def test_get_consultation_history(lead_id: int):
    """상담 이력 조회 테스트"""
    print("\n8. 상담 이력 조회 테스트")
    
    response = requests.get(f"{BASE_URL}/customer-leads/{lead_id}/consultations", headers=headers)
    print_response(response, "상담 이력 목록")

def test_get_reregistration_targets():
    """재등록 대상 조회 테스트"""
    print("\n9. 재등록 대상 조회 테스트")
    
    response = requests.get(f"{BASE_URL}/customer-leads/reregistration-targets", headers=headers)
    print_response(response, "재등록 대상 목록")

def test_assign_staff_bulk():
    """담당자 일괄 지정 테스트"""
    print("\n10. 담당자 일괄 지정 테스트")
    
    # 먼저 유입고객 몇 개의 ID를 가져옴
    response = requests.get(f"{BASE_URL}/customer-leads/", params={"page_size": 3}, headers=headers)
    
    if response.status_code == 200:
        items = response.json()["items"]
        if items:
            lead_ids = [item["lead_id"] for item in items[:3]]
            
            assign_data = {
                "lead_ids": lead_ids,
                "staff_id": 1  # 실제 존재하는 staff_id로 변경 필요
            }
            
            response = requests.post(f"{BASE_URL}/customer-leads/assign-staff", json=assign_data, headers=headers)
            print_response(response, "담당자 일괄 지정")

def test_export_data():
    """데이터 내보내기 테스트"""
    print("\n11. 데이터 내보내기 테스트")
    
    # Excel 형식으로 내보내기
    response = requests.get(f"{BASE_URL}/customer-leads/export?format=excel", headers=headers)
    
    if response.status_code == 200:
        with open("exported_leads.xlsx", "wb") as f:
            f.write(response.content)
        print("✅ Excel 파일로 내보내기 성공: exported_leads.xlsx")
    else:
        print(f"❌ 내보내기 실패: {response.status_code}")

def test_error_cases():
    """에러 케이스 테스트"""
    print("\n12. 에러 케이스 테스트")
    
    # 존재하지 않는 리드 조회
    response = requests.get(f"{BASE_URL}/customer-leads/99999", headers=headers)
    print_response(response, "존재하지 않는 리드 조회")
    
    # 중복된 전화번호로 생성 시도
    duplicate_lead = {
        "name": "중복 테스트",
        "phone": "010-1234-5678",  # 이미 생성한 번호
        "lead_date": str(date.today())
    }
    response = requests.post(f"{BASE_URL}/customer-leads/", json=duplicate_lead, headers=headers)
    print_response(response, "중복 전화번호 생성 시도")

def main():
    """메인 테스트 실행"""
    print("="*60)
    print("유입고객 관리 API 테스트")
    print("="*60)
    
    # 1. 인증
    if not test_authentication():
        print("인증 실패로 테스트를 중단합니다.")
        return
    
    # 2. 목록 조회
    test_get_customer_leads()
    
    # 3. 통계 조회
    test_get_statistics()
    
    # 4. 생성
    lead_id = test_create_customer_lead()
    
    if lead_id:
        # 5. 상세 조회
        test_get_customer_lead_detail(lead_id)
        
        # 6. 수정
        test_update_customer_lead(lead_id)
        
        # 7. 상담 이력 추가
        test_add_consultation_history(lead_id)
        
        # 8. 상담 이력 조회
        test_get_consultation_history(lead_id)
    
    # 9. 재등록 대상 조회
    test_get_reregistration_targets()
    
    # 10. 담당자 일괄 지정
    test_assign_staff_bulk()
    
    # 11. 데이터 내보내기
    test_export_data()
    
    # 12. 에러 케이스
    test_error_cases()
    
    print("\n✅ 모든 테스트 완료!")

if __name__ == "__main__":
    main()