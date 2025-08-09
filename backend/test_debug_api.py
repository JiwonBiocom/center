"""디버그용 API 테스트"""
import requests
import json

# 로그인
login_response = requests.post("http://localhost:8000/api/v1/auth/login", data={
    "username": "admin@aibio.com",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 목록 조회
    response = requests.get("http://localhost:8000/api/v1/customer-leads/?page=1&page_size=2", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")  # 처음 500자만
else:
    print("Login failed")