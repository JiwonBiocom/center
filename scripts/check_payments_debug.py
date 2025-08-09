#!/usr/bin/env python3
"""
결제 데이터 디버깅
"""
import requests

API_URL = "https://center-production-1421.up.railway.app"

def check_payments():
    """결제 데이터 확인"""
    
    print("🔍 결제 데이터 디버깅")
    print("=" * 50)
    
    # 1. 기본 API 확인
    print("\n1️⃣ Payments API 확인:")
    response = requests.get(f"{API_URL}/api/v1/payments/?limit=5")
    print(f"   상태 코드: {response.status_code}")
    print(f"   응답: {response.text[:200]}")
    
    # 2. 총 개수 확인
    print("\n2️⃣ Payments Count 확인:")
    response = requests.get(f"{API_URL}/api/v1/payments/count")
    print(f"   상태 코드: {response.status_code}")
    print(f"   응답: {response.text}")
    
    # 3. Health Check
    print("\n3️⃣ Health Check:")
    response = requests.get(f"{API_URL}/health")
    print(f"   상태 코드: {response.status_code}")
    print(f"   응답: {response.text}")
    
    # 4. API Docs 확인
    print("\n4️⃣ API Docs 접근 가능 여부:")
    response = requests.get(f"{API_URL}/docs")
    print(f"   상태 코드: {response.status_code}")
    
    # 5. 특정 고객의 결제 확인
    print("\n5️⃣ 특정 고객(ID: 618)의 결제 확인:")
    response = requests.get(f"{API_URL}/api/v1/customers/618/payments")
    print(f"   상태 코드: {response.status_code}")
    print(f"   응답: {response.text[:200]}")

if __name__ == "__main__":
    check_payments()