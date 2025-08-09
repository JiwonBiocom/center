#!/usr/bin/env python3
"""
인증 테스트 스크립트
다양한 계정으로 로그인을 시도하고 토큰을 확인합니다.
"""

import requests
import json
from typing import Optional, Dict

# API 기본 URL
API_URL = "https://center-production-1421.up.railway.app"

# 테스트할 계정 목록
TEST_ACCOUNTS = [
    {"email": "admin@aibio.kr", "password": "admin123", "name": "기본 admin"},
    {"email": "taejun@biocom.kr", "password": "admin1234", "name": "마스터 계정"},
    {"email": "manager@aibio.kr", "password": "manager123", "name": "매니저 계정"},
]

def test_login(email: str, password: str) -> Optional[Dict]:
    """로그인 테스트"""
    url = f"{API_URL}/api/v1/auth/login"

    try:
        response = requests.post(url, json={"email": email, "password": password})

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "token": data.get("data", {}).get("access_token"),
                "user": data.get("data", {}).get("user", {}),
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", {}).get("message", "Unknown error"),
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": -1
        }

def test_protected_endpoint(token: str, endpoint: str) -> Dict:
    """보호된 엔드포인트 테스트"""
    url = f"{API_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": -1,
            "success": False,
            "error": str(e)
        }

def main():
    print("=" * 60)
    print("AIBIO 센터 - 인증 시스템 테스트")
    print("=" * 60)

    # 1. 로그인 테스트
    print("\n1️⃣ 로그인 테스트")
    print("-" * 40)

    successful_logins = []

    for account in TEST_ACCOUNTS:
        print(f"\n테스트: {account['name']} ({account['email']})")
        result = test_login(account["email"], account["password"])

        if result["success"]:
            print(f"✅ 로그인 성공!")
            print(f"   - 사용자: {result['user'].get('name', 'Unknown')}")
            print(f"   - 권한: {result['user'].get('role', 'Unknown')}")
            print(f"   - 토큰: {result['token'][:20]}...")
            successful_logins.append({
                "account": account,
                "token": result["token"],
                "user": result["user"]
            })
        else:
            print(f"❌ 로그인 실패: {result['error']} (상태 코드: {result['status_code']})")

    # 2. 보호된 엔드포인트 테스트
    if successful_logins:
        print("\n\n2️⃣ 보호된 엔드포인트 접근 테스트")
        print("-" * 40)

        # 테스트할 엔드포인트
        test_endpoints = [
            "/api/v1/dashboard/stats",
            "/api/v1/services/usage",
            "/api/v1/notifications",
            "/api/v1/settings/users",
            "/api/v1/master/users"
        ]

        for login_info in successful_logins[:1]:  # 첫 번째 성공한 계정으로만 테스트
            print(f"\n계정: {login_info['account']['name']}")
            print(f"권한: {login_info['user'].get('role', 'Unknown')}")

            for endpoint in test_endpoints:
                result = test_protected_endpoint(login_info["token"], endpoint)
                emoji = "✅" if result["success"] else "❌"
                print(f"{emoji} {endpoint}: {result['status_code']}")

    # 3. 현재 사용자 확인
    print("\n\n3️⃣ 현재 사용자 정보 확인")
    print("-" * 40)

    for login_info in successful_logins:
        token = login_info["token"]
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(f"{API_URL}/api/v1/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json().get("data", {})
                print(f"\n계정: {login_info['account']['email']}")
                print(f"  - ID: {user_data.get('user_id')}")
                print(f"  - 이름: {user_data.get('name')}")
                print(f"  - 권한: {user_data.get('role')}")
                print(f"  - 활성: {user_data.get('is_active')}")
        except Exception as e:
            print(f"❌ 사용자 정보 조회 실패: {e}")

if __name__ == "__main__":
    main()
