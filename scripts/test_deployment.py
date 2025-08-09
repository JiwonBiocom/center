#!/usr/bin/env python3
"""배포 상태 테스트 스크립트"""
import requests
import json
import sys
from datetime import datetime

# 배포 URL
FRONTEND_URL = "https://center-ten.vercel.app"
BACKEND_URL = "https://center-production-1421.up.railway.app"

def test_backend_health():
    """백엔드 헬스체크"""
    print("1. 백엔드 헬스체크...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ 백엔드 정상 작동")
            return True
        else:
            print(f"   ❌ 백엔드 응답 코드: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 백엔드 연결 실패: {e}")
        return False

def test_cors_headers():
    """CORS 헤더 테스트"""
    print("\n2. CORS 헤더 테스트...")
    headers = {
        "Origin": FRONTEND_URL,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.options(
            f"{BACKEND_URL}/api/v1/auth/login",
            headers=headers,
            timeout=10
        )
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods")
        }
        
        print(f"   CORS 헤더:")
        for key, value in cors_headers.items():
            if value:
                print(f"   ✅ {key}: {value}")
            else:
                print(f"   ❌ {key}: 없음")
        
        return cors_headers["Access-Control-Allow-Origin"] == FRONTEND_URL
    except Exception as e:
        print(f"   ❌ CORS 테스트 실패: {e}")
        return False

def test_security_headers():
    """보안 헤더 테스트"""
    print("\n3. 보안 헤더 테스트...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        
        security_headers = {
            "Content-Security-Policy": response.headers.get("Content-Security-Policy"),
            "Strict-Transport-Security": response.headers.get("Strict-Transport-Security"),
            "X-Content-Type-Options": response.headers.get("X-Content-Type-Options"),
            "X-Frame-Options": response.headers.get("X-Frame-Options"),
            "X-XSS-Protection": response.headers.get("X-XSS-Protection")
        }
        
        print(f"   보안 헤더:")
        all_present = True
        for key, value in security_headers.items():
            if value:
                print(f"   ✅ {key}: {value[:50]}...")
            else:
                print(f"   ❌ {key}: 없음")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"   ❌ 보안 헤더 테스트 실패: {e}")
        return False

def test_login_api():
    """로그인 API 테스트"""
    print("\n4. 로그인 API 테스트...")
    
    login_data = {
        "username": "admin@aibio.kr",
        "password": "admin123"
    }
    
    headers = {
        "Origin": FRONTEND_URL,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json=login_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ 로그인 성공")
            data = response.json()
            if "access_token" in data:
                print(f"   ✅ 액세스 토큰 발급됨")
                return data["access_token"]
        else:
            print(f"   ❌ 로그인 실패: {response.status_code}")
            print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   ❌ 로그인 API 호출 실패: {e}")
    
    return None

def test_notifications_api(token):
    """알림 API 테스트"""
    print("\n5. 알림 API 테스트...")
    
    if not token:
        print("   ⚠️  토큰이 없어 테스트 건너뜀")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": FRONTEND_URL
    }
    
    # 알림 목록 테스트
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/notifications",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ 알림 목록 조회 성공")
        else:
            print(f"   ❌ 알림 목록 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 알림 목록 API 호출 실패: {e}")
    
    # 알림 통계 테스트
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/notifications/stats",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ 알림 통계 조회 성공")
            stats = response.json()
            print(f"   전체: {stats.get('total', 0)}, 읽지않음: {stats.get('unread', 0)}")
        else:
            print(f"   ❌ 알림 통계 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 알림 통계 API 호출 실패: {e}")

def main():
    """메인 테스트 실행"""
    print(f"🚀 배포 테스트 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    print("=" * 60)
    
    # 테스트 실행
    backend_ok = test_backend_health()
    cors_ok = test_cors_headers()
    security_ok = test_security_headers()
    token = test_login_api()
    
    if token:
        test_notifications_api(token)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약:")
    print(f"✅ 백엔드 헬스체크: {'통과' if backend_ok else '실패'}")
    print(f"✅ CORS 설정: {'통과' if cors_ok else '실패'}")
    print(f"✅ 보안 헤더: {'통과' if security_ok else '실패'}")
    print(f"✅ 로그인 API: {'통과' if token else '실패'}")
    
    if not (backend_ok and cors_ok and token):
        sys.exit(1)

if __name__ == "__main__":
    main()