#!/usr/bin/env python3
"""
Railway에서 직접 데이터베이스 상태 확인
"""
import requests
import json

API_URL = "https://center-production-1421.up.railway.app"

def check_database_directly():
    """데이터베이스 직접 확인"""
    
    print("🔍 Railway 데이터베이스 직접 확인")
    print("=" * 50)
    
    # 1. 로그인
    login_response = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json={"email": "admin@aibio.kr", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ 로그인 실패")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Debug 엔드포인트로 직접 쿼리
    queries = [
        "SELECT COUNT(*) as count FROM payments",
        "SELECT COUNT(*) as count FROM customers",
        "SELECT schemaname, tablename FROM pg_tables WHERE tablename = 'payments'",
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'payments'",
        "SELECT payment_id, customer_id, payment_date, amount FROM payments LIMIT 5"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. 쿼리: {query}")
        
        # Debug SQL 엔드포인트가 있다면 사용
        debug_url = f"{API_URL}/api/v1/debug/sql"
        response = requests.post(
            debug_url, 
            json={"query": query},
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"   결과: {response.json()}")
        else:
            # 대안: 일반 API로 확인
            if "COUNT" in query and "payments" in query:
                response = requests.get(f"{API_URL}/api/v1/payments/", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   결과: 총 {len(data)}건")
                    
def check_railway_logs():
    """Railway 로그 확인 힌트"""
    
    print("\n💡 Railway 대시보드에서 확인할 사항:")
    print("1. center 프로젝트 → Logs 탭")
    print("2. 최근 로그에서 다음 검색:")
    print("   - 'payment' 또는 'Payment'")
    print("   - 'INSERT INTO payments'")
    print("   - 'ERROR' 또는 'error'")
    print("\n3. 특히 GitHub Actions 실행 시간대 로그 확인")

if __name__ == "__main__":
    check_database_directly()
    check_railway_logs()