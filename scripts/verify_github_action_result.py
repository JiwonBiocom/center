#!/usr/bin/env python3
"""
GitHub Actions 실행 결과 검증
"""
import requests
import json

def check_via_api():
    """API를 통한 데이터 확인"""
    
    print("🔍 GitHub Actions 실행 결과 검증")
    print("=" * 50)
    
    # Admin 로그인
    login_url = "https://center-production-1421.up.railway.app/api/v1/auth/login"
    login_data = {
        "email": "admin@aibio.kr",
        "password": "admin123"
    }
    
    print("\n1️⃣ Admin 로그인 시도...")
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ 로그인 성공")
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # 결제 데이터 확인
        print("\n2️⃣ 결제 데이터 확인...")
        response = requests.get(
            "https://center-production-1421.up.railway.app/api/v1/payments/",
            headers=headers
        )
        
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            payments = response.json()
            print(f"   결제 건수: {len(payments)}건")
            
            if len(payments) > 0:
                print("\n   샘플 데이터 (처음 3개):")
                for i, payment in enumerate(payments[:3]):
                    print(f"   {i+1}. ID: {payment.get('payment_id')} | {payment.get('payment_date')} | ₩{payment.get('amount'):,.0f}")
            else:
                print("   ⚠️ 결제 데이터가 없습니다")
                
                # 추가 디버깅
                print("\n3️⃣ 데이터베이스 직접 조회 시도...")
                debug_response = requests.get(
                    "https://center-production-1421.up.railway.app/api/v1/debug/payments",
                    headers=headers
                )
                
                if debug_response.status_code == 200:
                    print(f"   디버그 응답: {debug_response.text[:200]}")
    else:
        print(f"❌ 로그인 실패: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    check_via_api()