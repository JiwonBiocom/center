#!/usr/bin/env python3
"""
Vercel 서버 간단한 로딩 시간 측정
"""
import time
import requests
from datetime import datetime

VERCEL_URL = "https://center-ten.vercel.app"

def measure_response_time(url, name):
    """URL 응답 시간 측정"""
    print(f"\n🔍 {name} 측정 중...")
    
    times = []
    for i in range(5):
        start = time.time()
        try:
            response = requests.get(url, timeout=30)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  시도 {i+1}: {elapsed:.2f}초 (상태: {response.status_code})")
            
            # 첫 번째 시도에서 콘텐츠 크기 확인
            if i == 0 and response.status_code == 200:
                content_length = len(response.content)
                print(f"  콘텐츠 크기: {content_length / 1024:.1f} KB")
        except Exception as e:
            print(f"  시도 {i+1}: 실패 - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n📊 평균 응답 시간: {avg_time:.2f}초")
        
        # 평가
        if avg_time < 1.0:
            evaluation = "⚡ 매우 빠름 (1초 미만)"
        elif avg_time < 2.0:
            evaluation = "✅ 빠름 (2초 미만)"
        elif avg_time < 3.0:
            evaluation = "🔶 보통 (3초 미만)"
        elif avg_time < 5.0:
            evaluation = "⚠️ 느림 (5초 미만)"
        else:
            evaluation = "❌ 매우 느림 (5초 이상)"
        
        print(f"평가: {evaluation}")
        return avg_time, evaluation
    else:
        return None, "측정 실패"

def check_api_endpoints():
    """API 엔드포인트 확인"""
    print("\n🌐 API 엔드포인트 확인:")
    
    endpoints = [
        "/api/v1/customers/",
        "/api/v1/payments/stats/summary",
        "/api/v1/packages/"
    ]
    
    for endpoint in endpoints:
        url = VERCEL_URL + endpoint
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start
            print(f"  {endpoint}: {elapsed:.3f}초 (상태: {response.status_code})")
        except Exception as e:
            print(f"  {endpoint}: 실패 - {e}")

def main():
    print(f"🚀 Vercel 배포 서버 성능 측정 (간단 버전)")
    print(f"URL: {VERCEL_URL}")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 메인 페이지 (대시보드)
    dashboard_time, dashboard_eval = measure_response_time(VERCEL_URL + "/", "대시보드 페이지")
    
    # 2. 고객 관리 페이지
    customers_time, customers_eval = measure_response_time(VERCEL_URL + "/customers", "고객 관리 페이지")
    
    # 3. API 엔드포인트 확인
    check_api_endpoints()
    
    # 요약
    print("\n" + "=" * 60)
    print("📊 측정 요약:")
    print(f"\n1. 대시보드 페이지:")
    if dashboard_time:
        print(f"   - 평균 로딩 시간: {dashboard_time:.2f}초")
        print(f"   - 평가: {dashboard_eval}")
    
    print(f"\n2. 고객 관리 페이지:")
    if customers_time:
        print(f"   - 평균 로딩 시간: {customers_time:.2f}초")
        print(f"   - 평가: {customers_eval}")
    
    if dashboard_time and customers_time:
        print(f"\n🔍 비교:")
        if dashboard_time < customers_time:
            print(f"   - 대시보드가 {customers_time - dashboard_time:.2f}초 더 빠름")
        else:
            print(f"   - 고객 관리가 {dashboard_time - customers_time:.2f}초 더 빠름")
    
    print("\n💡 참고:")
    print("- 이 측정은 HTML 다운로드 시간만 포함합니다")
    print("- 실제 사용자가 느끼는 시간은 JavaScript 실행과 렌더링 시간이 추가됩니다")
    print("- Vercel Edge Network의 위치에 따라 속도가 달라질 수 있습니다")

if __name__ == "__main__":
    main()