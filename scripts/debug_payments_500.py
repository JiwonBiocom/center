#!/usr/bin/env python3
"""
Payments API 500 에러 디버깅
"""
import requests
import json

API_URL = "https://center-production-1421.up.railway.app"

def debug_payments_api():
    """결제 API 디버깅"""
    
    print("🔍 Payments API 500 에러 디버깅")
    print("=" * 50)
    
    # 1. 통계 API (정상 작동)
    print("\n1️⃣ 통계 API 테스트:")
    response = requests.get(f"{API_URL}/api/v1/payments/stats")
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"   결과: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 2. 목록 API (500 에러)
    print("\n2️⃣ 목록 API 테스트:")
    response = requests.get(f"{API_URL}/api/v1/payments/?limit=1")
    print(f"   상태: {response.status_code}")
    print(f"   응답: {response.text}")
    
    # 3. 다양한 파라미터로 테스트
    print("\n3️⃣ 다양한 조건으로 테스트:")
    
    # 3-1. limit 없이
    response = requests.get(f"{API_URL}/api/v1/payments/")
    print(f"   - limit 없이: {response.status_code}")
    
    # 3-2. skip=0 명시
    response = requests.get(f"{API_URL}/api/v1/payments/?skip=0&limit=1")
    print(f"   - skip=0 명시: {response.status_code}")
    
    # 3-3. 특정 고객
    response = requests.get(f"{API_URL}/api/v1/customers/618/payments")
    print(f"   - 특정 고객(618): {response.status_code}")
    
    # 4. 로그인 후 테스트
    print("\n4️⃣ 인증 후 테스트:")
    login_response = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json={"email": "admin@aibio.kr", "password": "admin123"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{API_URL}/api/v1/payments/?limit=1", headers=headers)
        print(f"   - 인증된 요청: {response.status_code}")
        if response.status_code != 200:
            print(f"   - 에러 내용: {response.text}")

if __name__ == "__main__":
    debug_payments_api()