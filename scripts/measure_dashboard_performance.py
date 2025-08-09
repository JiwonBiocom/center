#!/usr/bin/env python3
"""
대시보드 성능 측정 스크립트
최적화 전후 성능을 비교합니다.
"""
from playwright.sync_api import sync_playwright
import time
from datetime import datetime

def measure_dashboard_performance():
    """대시보드 로딩 성능 측정"""
    
    print(f"🚀 대시보드 성능 측정 시작")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 네트워크 모니터링 활성화
        network_requests = []
        
        def on_request(request):
            if '/api/v1/' in request.url:
                network_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'start_time': time.time()
                })
        
        def on_response(response):
            if '/api/v1/' in response.url:
                for req in network_requests:
                    if req['url'] == response.url:
                        req['status'] = response.status
                        req['duration'] = (time.time() - req['start_time']) * 1000
                        break
        
        page.on('request', on_request)
        page.on('response', on_response)
        
        # 로그인
        print("\n1. 로그인 중...")
        page.goto('https://center-coral-five.vercel.app/login')
        page.wait_for_selector('input[type="email"]', timeout=10000)
        page.fill('input[type="email"]', 'admin@aibio.kr')
        page.fill('input[type="password"]', 'admin123')
        page.click('button[type="submit"]')
        
        # 대시보드로 이동하기 전 초기화
        page.wait_for_timeout(2000)
        network_requests.clear()
        
        # 대시보드 로딩 시간 측정
        print("\n2. 대시보드 로딩 측정...")
        start_time = time.time()
        
        # 대시보드 클릭
        page.click('text="대시보드"')
        
        # 주요 컴포넌트가 로드될 때까지 대기
        page.wait_for_selector('.dashboard-stats', timeout=10000)
        page.wait_for_selector('canvas', timeout=10000)  # 차트
        
        total_time = (time.time() - start_time) * 1000
        
        # 결과 출력
        print(f"\n📊 측정 결과:")
        print(f"  - 전체 로딩 시간: {total_time:.0f}ms ({total_time/1000:.1f}초)")
        
        print(f"\n📡 API 요청 분석:")
        api_times = []
        for req in network_requests:
            if 'duration' in req:
                endpoint = req['url'].split('/api/v1/')[1].split('?')[0]
                print(f"  - {endpoint}: {req['duration']:.0f}ms")
                api_times.append(req['duration'])
        
        if api_times:
            print(f"\n  총 API 요청 수: {len(api_times)}개")
            print(f"  평균 응답 시간: {sum(api_times)/len(api_times):.0f}ms")
            print(f"  최대 응답 시간: {max(api_times):.0f}ms")
        
        # 최적화 전후 비교
        print(f"\n🎯 성능 개선 결과:")
        print(f"  최적화 전: 약 5초")
        print(f"  최적화 후: {total_time/1000:.1f}초")
        print(f"  개선율: {((5000 - total_time) / 5000 * 100):.0f}%")
        
        # 스크린샷
        page.screenshot(path='dashboard_optimized.png')
        print(f"\n📸 스크린샷 저장: dashboard_optimized.png")
        
        browser.close()

if __name__ == "__main__":
    measure_dashboard_performance()