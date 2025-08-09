#!/usr/bin/env python
"""
생성된 사용자 계정 로그인 테스트
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login(email: str, password: str):
    """로그인 테스트"""
    print(f"\n테스트: {email}")
    print("-" * 50)
    
    # 로그인 시도
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={
            "username": email,
            "password": password
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 로그인 성공!")
        print(f"   - 토큰 타입: {data.get('token_type')}")
        print(f"   - 액세스 토큰: {data.get('access_token')[:20]}...")
        
        # 토큰으로 사용자 정보 확인
        headers = {"Authorization": f"Bearer {data.get('access_token')}"}
        me_response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"   - 사용자 정보: {user_info.get('name')} ({user_info.get('role')})")
            return True
    else:
        print(f"❌ 로그인 실패: {response.status_code}")
        print(f"   - 오류: {response.text}")
        return False
    
    return False

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("사용자 계정 로그인 테스트")
    print("=" * 70)
    
    # 테스트할 계정 목록
    test_accounts = [
        {"email": "clv@biocom.kr", "password": "admin123", "name": "Admin (기존)"},
        {"email": "sookyeong@biocom.kr", "password": "1111", "name": "이수경 (매니저)"},
        {"email": "seungwoo@biocom.kr", "password": "1111", "name": "유승우 (관리자)"},
        {"email": "yerim@biocom.kr", "password": "1111", "name": "김예림 (매니저)"},
        {"email": "taejun@biocom.kr", "password": "admin123", "name": "전태준 (관리자)"}
    ]
    
    success_count = 0
    
    for account in test_accounts:
        if test_login(account["email"], account["password"]):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"테스트 결과: {success_count}/{len(test_accounts)} 성공")
    print("=" * 70)

if __name__ == "__main__":
    main()