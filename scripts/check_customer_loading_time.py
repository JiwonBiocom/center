#!/usr/bin/env python3
"""
고객 관리 페이지 로딩 시간 측정
"""
import time
import requests
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright

# API 엔드포인트
API_BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:5173"

def measure_api_response_time():
    """고객 목록 API 응답 시간 측정"""
    print("🔍 API 응답 시간 측정 중...")
    
    # 기본 정렬 (최근 방문 순)
    params = {
        "skip": 0,
        "limit": 20,
        "sort_by": "last_visit_date",
        "sort_order": "desc"
    }
    
    # 5번 측정하여 평균 계산
    times = []
    for i in range(5):
        start = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/customers/", params=params)
            response.raise_for_status()
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  시도 {i+1}: {elapsed:.3f}초")
        except Exception as e:
            print(f"  시도 {i+1}: 실패 - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n📊 API 평균 응답 시간: {avg_time:.3f}초")
        
        # 성능 평가
        if avg_time < 0.1:
            evaluation = "⚡ 매우 빠름 (100ms 미만)"
        elif avg_time < 0.3:
            evaluation = "✅ 빠름 (300ms 미만)"
        elif avg_time < 0.5:
            evaluation = "🔶 보통 (500ms 미만)"
        elif avg_time < 1.0:
            evaluation = "⚠️ 느림 (1초 미만)"
        else:
            evaluation = "❌ 매우 느림 (1초 이상)"
        
        print(f"평가: {evaluation}")
        
        # 응답 데이터 확인
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                print(f"반환된 고객 수: {len(data['data'])}개")
                print(f"전체 고객 수: {data.get('total', 'N/A')}명")

async def measure_frontend_loading_time():
    """프론트엔드 페이지 로딩 시간 측정"""
    print("\n🌐 프론트엔드 로딩 시간 측정 중...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # 네트워크 요청 모니터링
        api_requests = []
        
        async def handle_request(request):
            if '/api/v1/customers' in request.url:
                api_requests.append({
                    'url': request.url,
                    'start': time.time()
                })
        
        async def handle_response(response):
            for req in api_requests:
                if req['url'] == response.url:
                    req['end'] = time.time()
                    req['duration'] = req['end'] - req['start']
                    req['status'] = response.status
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # 페이지 로딩 시간 측정
        start_time = time.time()
        
        try:
            # 고객 관리 페이지로 이동
            await page.goto(f"{FRONTEND_URL}/customers", wait_until='networkidle')
            
            # 테이블이 렌더링될 때까지 대기
            await page.wait_for_selector('table', timeout=10000)
            
            # 고객 데이터가 로드될 때까지 대기
            await page.wait_for_selector('tbody tr', timeout=10000)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n📊 전체 페이지 로딩 시간: {total_time:.3f}초")
            
            # 성능 평가
            if total_time < 1.0:
                evaluation = "⚡ 매우 빠름 (1초 미만)"
            elif total_time < 2.0:
                evaluation = "✅ 빠름 (2초 미만)"
            elif total_time < 3.0:
                evaluation = "🔶 보통 (3초 미만)"
            elif total_time < 5.0:
                evaluation = "⚠️ 느림 (5초 미만)"
            else:
                evaluation = "❌ 매우 느림 (5초 이상)"
            
            print(f"평가: {evaluation}")
            
            # API 요청 분석
            if api_requests:
                print(f"\n🔍 API 요청 분석:")
                for req in api_requests:
                    if 'duration' in req:
                        print(f"  - {req['url'].split('?')[0]}: {req['duration']:.3f}초 (상태: {req['status']})")
            
            # 렌더링된 고객 수 확인
            customer_rows = await page.query_selector_all('tbody tr')
            print(f"\n렌더링된 고객 수: {len(customer_rows)}개")
            
            # 정렬 상태 확인
            sort_buttons = await page.query_selector_all('button[class*="flex items-center gap-1"]')
            if sort_buttons:
                print("\n정렬 가능한 컬럼:")
                for button in sort_buttons:
                    text = await button.text_content()
                    print(f"  - {text.strip()}")
            
            # 스크린샷 저장
            await page.screenshot(path='customer_page_loaded.png')
            print("\n📸 스크린샷 저장: customer_page_loaded.png")
            
        except Exception as e:
            print(f"❌ 로딩 실패: {e}")
        
        await browser.close()

async def main():
    print(f"🚀 고객 관리 페이지 성능 측정 시작")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # API 응답 시간 측정
    measure_api_response_time()
    
    # 프론트엔드 로딩 시간 측정
    await measure_frontend_loading_time()
    
    print("\n" + "=" * 60)
    print("✅ 측정 완료")

if __name__ == "__main__":
    asyncio.run(main())