#!/usr/bin/env python3
"""
Railway 백엔드 API를 통해 결제 데이터 시딩
실행: python scripts/seed_via_railway_api.py
"""
import requests
import json

# Railway 백엔드 URL
API_BASE_URL = "https://center-production-1421.up.railway.app"

def check_schema():
    """데이터베이스 스키마 정보 확인"""
    
    print("🔍 데이터베이스 스키마 확인 중...")
    
    # Debug API를 통해 스키마 정보 가져오기
    response = requests.get(f"{API_BASE_URL}/api/v1/debug/schema/payments")
    
    if response.status_code == 200:
        schema_info = response.json()
        print("\n📋 payments 테이블 스키마:")
        for col in schema_info.get('columns', []):
            print(f"  - {col['name']} ({col['type']})")
        return schema_info
    else:
        print(f"❌ 스키마 확인 실패: {response.status_code}")
        return None

def get_enum_values():
    """payment_type enum 값 확인"""
    
    print("\n🔍 payment_type enum 값 확인 중...")
    
    # SQL 실행을 통해 enum 값 확인
    response = requests.post(
        f"{API_BASE_URL}/api/v1/debug/sql",
        json={
            "query": """
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'payment_type'
                )
            """
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ payment_type 가능한 값:")
        for row in result.get('rows', []):
            print(f"  - {row[0]}")
        return result
    else:
        print(f"❌ enum 값 확인 실패: {response.status_code}")
        return None

def main():
    """메인 실행 함수"""
    
    print("🚀 Railway API를 통한 스키마 분석")
    print("=" * 50)
    
    # 스키마 확인
    schema = check_schema()
    
    # enum 값 확인
    enum_values = get_enum_values()
    
    print("\n💡 다음 단계:")
    print("1. payment_type의 올바른 enum 값 확인")
    print("2. SQL 스크립트 수정")
    print("3. Supabase SQL Editor에서 실행")

if __name__ == "__main__":
    main()