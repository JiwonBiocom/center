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

def test_service_stats_multiple_months():
    """여러 달의 서비스 통계 API 테스트"""
    token = login_and_get_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 여러 달 테스트
    test_months = [
        (2024, 5),  # 2024년 5월
        (2024, 12), # 2024년 12월
        (2025, 1),  # 2025년 1월
    ]
    
    for year, month in test_months:
        params = {
            "year": year,
            "month": month
        }
        
        response = requests.get(f"{BASE_URL}/api/v1/services/stats", headers=headers, params=params)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"\nService Stats for {year}-{month:02d}:")
            print(f"  Total Services: {stats.get('total_services', 0)}")
            print(f"  Unique Customers: {stats.get('unique_customers', 0)}")
            print(f"  Most Popular Service: {stats.get('most_popular_service', 'N/A')}")
            print(f"  Total Revenue: {stats.get('total_revenue', 0):,}원")
            print(f"  Average Daily Services: {stats.get('average_daily_services', 0)}")
        else:
            print(f"\nAPI request failed for {year}-{month}: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    test_service_stats_multiple_months()