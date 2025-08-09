"""간단한 엔드포인트 테스트"""
import requests

# 로그인
login_response = requests.post("http://localhost:8000/api/v1/auth/login", data={
    "username": "admin@aibio.com",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. reregistration-targets 테스트
    print("1. 재등록 대상 조회")
    response = requests.get(
        "http://localhost:8000/api/v1/customer-leads/reregistration-targets",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text[:200]}")
    
    # 2. export 테스트
    print("\n2. 엑셀 내보내기")
    response = requests.get(
        "http://localhost:8000/api/v1/customer-leads/export",
        params={"format": "excel"},
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Success! File size: {len(response.content)} bytes")
    else:
        print(f"   Error: {response.text[:200]}")
else:
    print("Login failed")