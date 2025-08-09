#!/usr/bin/env python3
"""
API 서버 상태 확인
"""
import requests
import time

def check_api_servers():
    """API 서버들 상태 확인"""
    servers = [
        ("Railway (현재 사용중)", "https://center-production-1421.up.railway.app/api/v1"),
        ("로컬 서버", "http://localhost:8000/api/v1"),
    ]
    
    print("🔍 API 서버 상태 확인")
    print("=" * 60)
    
    for name, base_url in servers:
        print(f"\n📡 {name}")
        print(f"URL: {base_url}")
        
        # Health check
        try:
            start = time.time()
            response = requests.get(f"{base_url}/health", timeout=5)
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                print(f"✅ Health Check: {elapsed:.0f}ms")
            else:
                print(f"⚠️ Health Check: {response.status_code} ({elapsed:.0f}ms)")
        except Exception as e:
            print(f"❌ Health Check 실패: {e}")
        
        # Customers API
        try:
            start = time.time()
            response = requests.get(f"{base_url}/customers/?limit=1", timeout=10)
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('total', 0) if isinstance(data, dict) else len(data)
                print(f"✅ Customers API: {elapsed:.0f}ms (고객 수: {count})")
            else:
                print(f"❌ Customers API: {response.status_code} ({elapsed:.0f}ms)")
        except Exception as e:
            print(f"❌ Customers API 실패: {e}")
        
        # Payments API
        try:
            start = time.time()
            response = requests.get(f"{base_url}/payments/stats/summary", timeout=10)
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                print(f"✅ Payments API: {elapsed:.0f}ms")
            else:
                print(f"❌ Payments API: {response.status_code} ({elapsed:.0f}ms)")
        except Exception as e:
            print(f"❌ Payments API 실패: {e}")
    
    print(f"\n💡 권장사항:")
    print("1. Railway 서버가 느리면 로컬 서버로 전환")
    print("2. 유효한 테스트 계정 확인")
    print("3. API 응답 시간이 500ms 이상이면 최적화 필요")

if __name__ == "__main__":
    check_api_servers()