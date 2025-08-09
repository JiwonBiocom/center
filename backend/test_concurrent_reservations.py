"""
동시간대 다른 서비스 예약 테스트
"""
import requests
from datetime import datetime, date, time
import json

BASE_URL = "http://localhost:8000"

# 로그인
login_data = {
    "username": "admin@aibio.center",
    "password": "admin123!"
}

print("1. 로그인 중...")
response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 로그인 성공")
else:
    print(f"❌ 로그인 실패: {response.status_code}")
    print(response.json())
    exit()

# 2. 고객과 서비스 타입 조회
print("\n2. 기본 데이터 조회 중...")
customers = requests.get(f"{BASE_URL}/api/v1/customers", headers=headers).json()
services = requests.get(f"{BASE_URL}/api/v1/services/types", headers=headers).json()

if customers["items"] and services:
    customer_id = customers["items"][0]["customer_id"]
    customer_name = customers["items"][0]["name"]
    
    # 브레인과 펄스 서비스 찾기
    brain_service = next((s for s in services if "브레인" in s["service_name"]), None)
    pulse_service = next((s for s in services if "펄스" in s["service_name"]), None)
    
    if brain_service and pulse_service:
        print(f"✅ 고객: {customer_name}")
        print(f"✅ 브레인 서비스: {brain_service['service_name']}")
        print(f"✅ 펄스 서비스: {pulse_service['service_name']}")
    else:
        print("❌ 서비스 타입을 찾을 수 없습니다")
        exit()
else:
    print("❌ 고객 또는 서비스 정보가 없습니다")
    exit()

# 3. 같은 시간에 브레인 예약 생성
print("\n3. 브레인 예약 생성 중...")
reservation_data1 = {
    "customer_id": customer_id,
    "service_type_id": brain_service["service_type_id"],
    "reservation_date": "2025-06-10",
    "reservation_time": "14:00",
    "duration_minutes": 60,
    "customer_request": "동시간대 브레인 예약 테스트"
}

response1 = requests.post(
    f"{BASE_URL}/api/v1/reservations/",
    headers=headers,
    json=reservation_data1
)

if response1.status_code == 200:
    reservation1 = response1.json()
    print(f"✅ 브레인 예약 성공 (ID: {reservation1['reservation_id']})")
else:
    print(f"❌ 브레인 예약 실패: {response1.status_code}")
    print(response1.json())

# 4. 같은 시간에 펄스 예약 생성
print("\n4. 같은 시간에 펄스 예약 생성 중...")
reservation_data2 = {
    "customer_id": customer_id,
    "service_type_id": pulse_service["service_type_id"],
    "reservation_date": "2025-06-10",
    "reservation_time": "14:00",
    "duration_minutes": 45,
    "customer_request": "동시간대 펄스 예약 테스트"
}

response2 = requests.post(
    f"{BASE_URL}/api/v1/reservations/",
    headers=headers,
    json=reservation_data2
)

if response2.status_code == 200:
    reservation2 = response2.json()
    print(f"✅ 펄스 예약 성공 (ID: {reservation2['reservation_id']})")
    print("\n🎉 동시간대 다른 서비스 예약이 성공적으로 작동합니다!")
else:
    print(f"❌ 펄스 예약 실패: {response2.status_code}")
    print(response2.json())

# 5. 같은 시간에 또 다른 브레인 예약 시도 (실패해야 함)
print("\n5. 같은 시간에 또 다른 브레인 예약 시도 중...")
reservation_data3 = {
    "customer_id": customer_id,
    "service_type_id": brain_service["service_type_id"],
    "reservation_date": "2025-06-10",
    "reservation_time": "14:00",
    "duration_minutes": 60,
    "customer_request": "중복 브레인 예약 테스트"
}

response3 = requests.post(
    f"{BASE_URL}/api/v1/reservations/",
    headers=headers,
    json=reservation_data3
)

if response3.status_code == 409:
    print(f"✅ 예상대로 중복 예약이 차단되었습니다: {response3.json()['detail']}")
else:
    print(f"❌ 중복 예약이 차단되지 않았습니다: {response3.status_code}")

# 6. 예약 목록 확인
print("\n6. 생성된 예약 목록 확인...")
params = {
    "reservation_date": "2025-06-10"
}
response = requests.get(f"{BASE_URL}/api/v1/reservations/", headers=headers, params=params)
if response.status_code == 200:
    reservations = response.json()["items"]
    print(f"\n2025-06-10일 예약 목록:")
    for r in reservations:
        if r["reservation_time"] == "14:00:00":
            print(f"  - {r['reservation_time']} {r['service_name']} ({r['customer_name']})")

print("\n✅ 테스트 완료!")