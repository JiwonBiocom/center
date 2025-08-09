"""직접 API 호출 테스트"""
import requests
import traceback

# 로그인
login_response = requests.post("http://localhost:8000/api/v1/auth/login", data={
    "username": "admin@aibio.com",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 가장 단순한 호출
    print("1. 기본 호출 (파라미터 없음)")
    response = requests.get("http://localhost:8000/api/v1/customer-leads/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    
    # 간단한 페이지네이션만
    print("\n2. 페이지네이션만")
    response = requests.get(
        "http://localhost:8000/api/v1/customer-leads/",
        params={"page": 1, "page_size": 2},
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    
    # 정렬 파라미터 추가
    print("\n3. 정렬 파라미터 추가")
    response = requests.get(
        "http://localhost:8000/api/v1/customer-leads/",
        params={
            "page": 1,
            "page_size": 2,
            "sort_by": "lead_date",  # created_at 대신 lead_date 사용
            "sort_order": "desc"
        },
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    else:
        data = response.json()
        print(f"   Success! Total: {data['total']}")
else:
    print("Login failed")