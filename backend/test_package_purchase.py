#!/usr/bin/env python3
import requests
import json

# 로그인하여 토큰 받기
def login():
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "username": "admin@aibio.com",
        "password": "admin123"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.json()}")
        return None

# 패키지 구매 테스트
def test_package_purchase(token):
    from datetime import datetime, timedelta
    
    url = "http://localhost:8000/api/v1/packages/purchase"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    now = datetime.now()
    data = {
        "customer_id": 3814,
        "package_id": 30,
        "payment_method": "카드결제",
        "payment_amount": 1500000,
        "purchase_date": now.isoformat() + "Z",
        "start_date": now.isoformat() + "Z",
        "end_date": (now + timedelta(days=60)).isoformat() + "Z"
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    token = login()
    if token:
        print("Login successful!")
        test_package_purchase(token)
    else:
        print("Login failed!")