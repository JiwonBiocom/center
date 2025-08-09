#!/usr/bin/env python3
"""
프로덕션 환경에서 PATCH 메서드가 정상 작동하는지 테스트하는 스크립트

사용법:
    python scripts/test_production_patch.py --token YOUR_JWT_TOKEN --customer-id 543
"""
import argparse
import requests
import json
from datetime import datetime

# 프로덕션 URL (Railway)
PRODUCTION_URL = "https://center-production-1421.up.railway.app"

def test_patch_customer(token: str, customer_id: int, test_name: str = None):
    """고객 이름 PATCH 테스트"""
    
    print(f"\n🧪 프로덕션 PATCH 테스트 시작")
    print(f"📍 URL: {PRODUCTION_URL}/api/v1/customers/{customer_id}")
    print(f"🔑 Token: {token[:20]}...")
    
    # 1. 현재 고객 정보 조회
    print("\n1️⃣ 현재 고객 정보 조회...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    get_response = requests.get(
        f"{PRODUCTION_URL}/api/v1/customers/{customer_id}",
        headers=headers
    )
    
    if get_response.status_code != 200:
        print(f"❌ 고객 조회 실패: {get_response.status_code}")
        print(f"응답: {get_response.text}")
        return False
    
    customer = get_response.json()
    original_name = customer.get('name', 'Unknown')
    print(f"✅ 현재 이름: {original_name}")
    
    # 2. PATCH로 이름 변경
    if not test_name:
        test_name = f"{original_name}_테스트_{datetime.now().strftime('%H%M%S')}"
    
    print(f"\n2️⃣ PATCH로 이름 변경 시도...")
    print(f"새 이름: {test_name}")
    
    patch_response = requests.patch(
        f"{PRODUCTION_URL}/api/v1/customers/{customer_id}",
        headers=headers,
        json={"name": test_name}
    )
    
    print(f"응답 코드: {patch_response.status_code}")
    
    if patch_response.status_code == 405:
        print("❌ 405 Method Not Allowed - PATCH 메서드가 라우팅되지 않음")
        print("\n💡 대안: PUT 메서드 시도...")
        
        # PUT으로 재시도
        put_response = requests.put(
            f"{PRODUCTION_URL}/api/v1/customers/{customer_id}",
            headers=headers,
            json={"name": test_name}
        )
        
        if put_response.status_code == 200:
            print("✅ PUT 메서드는 작동함")
            return True
        else:
            print(f"❌ PUT도 실패: {put_response.status_code}")
            return False
            
    elif patch_response.status_code == 200:
        print("✅ PATCH 성공!")
        
        # 3. 변경 확인
        print("\n3️⃣ 변경사항 확인...")
        verify_response = requests.get(
            f"{PRODUCTION_URL}/api/v1/customers/{customer_id}",
            headers=headers
        )
        
        if verify_response.status_code == 200:
            updated_customer = verify_response.json()
            updated_name = updated_customer.get('name', '')
            
            if updated_name == test_name:
                print(f"✅ 이름이 성공적으로 변경됨: {updated_name}")
                return True
            else:
                print(f"❌ 이름 변경이 반영되지 않음")
                print(f"기대값: {test_name}")
                print(f"실제값: {updated_name}")
                return False
    else:
        print(f"❌ 예상치 못한 응답: {patch_response.status_code}")
        print(f"응답 내용: {patch_response.text}")
        return False

def test_options_method(token: str, customer_id: int):
    """OPTIONS 메서드로 허용된 메서드 확인"""
    print(f"\n🔍 OPTIONS 메서드로 허용된 메서드 확인...")
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    options_response = requests.options(
        f"{PRODUCTION_URL}/api/v1/customers/{customer_id}",
        headers=headers
    )
    
    if options_response.status_code == 200:
        allow_header = options_response.headers.get('Allow', '')
        print(f"✅ 허용된 메서드: {allow_header}")
        
        if 'PATCH' in allow_header:
            print("✅ PATCH 메서드가 허용 목록에 포함됨")
        else:
            print("❌ PATCH 메서드가 허용 목록에 없음")
    else:
        print(f"❌ OPTIONS 요청 실패: {options_response.status_code}")

def main():
    parser = argparse.ArgumentParser(description='프로덕션 PATCH 메서드 테스트')
    parser.add_argument('--token', required=True, help='JWT 인증 토큰')
    parser.add_argument('--customer-id', type=int, default=543, help='테스트할 고객 ID')
    parser.add_argument('--name', help='변경할 이름 (미지정시 자동 생성)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 프로덕션 PATCH 메서드 테스트")
    print("=" * 60)
    
    # OPTIONS 메서드 확인
    test_options_method(args.token, args.customer_id)
    
    # PATCH 테스트
    success = test_patch_customer(args.token, args.customer_id, args.name)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 테스트 성공!")
    else:
        print("❌ 테스트 실패!")
        print("\n🔧 권장 조치:")
        print("1. Nginx/프록시 설정에서 PATCH 메서드 허용 확인")
        print("2. FastAPI CORS 설정 확인")
        print("3. Railway 플랫폼 설정 확인")
    print("=" * 60)

if __name__ == "__main__":
    main()