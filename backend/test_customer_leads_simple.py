"""
유입고객 관리 API 간단 테스트
"""
import requests
import json
from datetime import date

# API 베이스 URL
BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """API 테스트"""
    print("유입고객 관리 API 테스트 시작...\n")
    
    # 1. 로그인
    print("1. 로그인 테스트")
    login_response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": "admin@aibio.com",  # email을 username으로 사용
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ 로그인 실패: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 로그인 성공!")
    
    # 2. 유입고객 목록 조회
    print("\n2. 유입고객 목록 조회")
    list_response = requests.get(f"{BASE_URL}/customer-leads/", headers=headers)
    if list_response.status_code == 200:
        data = list_response.json()
        print(f"✅ 목록 조회 성공! 총 {data['total']}명의 유입고객")
        print(f"   현재 페이지: {data['page']}/{data['total_pages']}")
    else:
        print(f"❌ 목록 조회 실패: {list_response.text}")
    
    # 3. 통계 조회
    print("\n3. 유입고객 통계 조회")
    stats_response = requests.get(f"{BASE_URL}/customer-leads/stats", headers=headers)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"✅ 통계 조회 성공!")
        print(f"   총 유입고객: {stats['total_count']}명")
        print(f"   전환 고객: {stats['converted_count']}명")
        print(f"   전환율: {stats['conversion_rate']}%")
    else:
        print(f"❌ 통계 조회 실패: {stats_response.text}")
    
    # 4. 유입고객 생성
    print("\n4. 새 유입고객 생성")
    new_lead = {
        "name": "API 테스트 고객",
        "phone": f"010-{date.today().strftime('%m%d')}-9999",
        "lead_date": str(date.today()),
        "age": 30,
        "region": "서울",
        "lead_channel": "인스타그램",
        "db_channel": "구글폼",
        "notes": "API 테스트로 생성"
    }
    
    create_response = requests.post(f"{BASE_URL}/customer-leads/", json=new_lead, headers=headers)
    if create_response.status_code == 200:
        lead = create_response.json()
        print(f"✅ 유입고객 생성 성공! ID: {lead['lead_id']}")
        
        # 5. 상담 이력 추가
        print("\n5. 상담 이력 추가")
        consultation = {
            "lead_id": lead['lead_id'],
            "consultation_type": "phone",
            "consultation_date": f"{date.today()}T15:00:00",
            "result": "관심있음",
            "notes": "패키지 설명 완료"
        }
        
        consult_response = requests.post(
            f"{BASE_URL}/customer-leads/{lead['lead_id']}/consultations", 
            json=consultation, 
            headers=headers
        )
        
        if consult_response.status_code == 200:
            print("✅ 상담 이력 추가 성공!")
        else:
            print(f"❌ 상담 이력 추가 실패: {consult_response.text}")
    else:
        print(f"❌ 유입고객 생성 실패: {create_response.text}")
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    test_api()