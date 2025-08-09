import requests
import json
from datetime import datetime

# API 서버 URL
BASE_URL = "http://localhost:8000"

def login_and_get_token():
    """로그인하여 토큰 가져오기"""
    login_data = {
        "username": "admin@aibio.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def test_service_stats():
    """서비스 통계 API 테스트"""
    token = login_and_get_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2025년 1월 통계 조회
    params = {
        "year": 2025,
        "month": 1
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/services/stats", headers=headers, params=params)
    
    if response.status_code == 200:
        stats = response.json()
        print("Service Stats for 2025-01:")
        print(f"Total Services: {stats.get('total_services', 0)}")
        print(f"Unique Customers: {stats.get('unique_customers', 0)}")
        print(f"Most Popular Service: {stats.get('most_popular_service', 'N/A')}")
        print(f"Total Revenue: {stats.get('total_revenue', 0):,}원")
        print(f"Average Daily Services: {stats.get('average_daily_services', 0)}")
    else:
        print(f"API request failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_service_stats()