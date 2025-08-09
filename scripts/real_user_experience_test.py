#!/usr/bin/env python3
"""
실제 사용자 경험 기반 로딩 시간 측정
"""
import asyncio
import time
from playwright.async_api import async_playwright

VERCEL_URL = "https://center-ten.vercel.app"

async def measure_real_loading_time():
    """실제 사용자 경험 측정"""
    async with async_playwright() as p:
        # 헤드리스 모드로 브라우저 실행
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # 1. 대시보드 측정
        print("🔍 대시보드 페이지 측정 중...")
        page = await context.new_page()
        
        dashboard_start = time.time()
        try:
            # 페이지 이동
            await page.goto(VERCEL_URL, wait_until='domcontentloaded', timeout=30000)
            dashboard_dom_time = time.time() - dashboard_start
            
            # 주요 콘텐츠가 표시될 때까지 대기
            try:
                await page.wait_for_selector('h1', timeout=5000)
                dashboard_content_time = time.time() - dashboard_start
                
                # 스크린샷
                await page.screenshot(path='vercel_dashboard.png')
                print(f"✅ 대시보드 DOM 로드: {dashboard_dom_time:.2f}초")
                print(f"✅ 대시보드 콘텐츠 표시: {dashboard_content_time:.2f}초")
                
                # 표시된 요소 확인
                title = await page.text_content('h1')
                print(f"   페이지 제목: {title}")
            except:
                print(f"⚠️ 대시보드 콘텐츠 로드 실패 (DOM은 {dashboard_dom_time:.2f}초에 로드됨)")
        except Exception as e:
            print(f"❌ 대시보드 로드 실패: {e}")
        
        await page.close()
        
        # 2. 고객 관리 측정
        print("\n🔍 고객 관리 페이지 측정 중...")
        page = await context.new_page()
        
        customers_start = time.time()
        try:
            # 페이지 이동
            await page.goto(VERCEL_URL + "/customers", wait_until='domcontentloaded', timeout=30000)
            customers_dom_time = time.time() - customers_start
            
            # 주요 콘텐츠가 표시될 때까지 대기
            try:
                await page.wait_for_selector('h1', timeout=5000)
                customers_content_time = time.time() - customers_start
                
                # 스크린샷
                await page.screenshot(path='vercel_customers.png')
                print(f"✅ 고객 관리 DOM 로드: {customers_dom_time:.2f}초")
                print(f"✅ 고객 관리 콘텐츠 표시: {customers_content_time:.2f}초")
                
                # 표시된 요소 확인
                title = await page.text_content('h1')
                print(f"   페이지 제목: {title}")
                
                # 테이블 확인
                tables = await page.query_selector_all('table')
                print(f"   테이블 개수: {len(tables)}")
            except:
                print(f"⚠️ 고객 관리 콘텐츠 로드 실패 (DOM은 {customers_dom_time:.2f}초에 로드됨)")
        except Exception as e:
            print(f"❌ 고객 관리 로드 실패: {e}")
        
        await page.close()
        
        # 3. 네트워크 상태 확인
        print("\n🌐 네트워크 성능 측정...")
        page = await context.new_page()
        
        # 네트워크 요청 추적
        requests = []
        
        def handle_request(request):
            if '/api/' in request.url:
                requests.append({
                    'url': request.url,
                    'method': request.method,
                    'start': time.time()
                })
        
        def handle_response(response):
            for req in requests:
                if req['url'] == response.url and 'end' not in req:
                    req['end'] = time.time()
                    req['duration'] = req['end'] - req['start']
                    req['status'] = response.status
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # 대시보드 다시 로드하여 API 요청 확인
        await page.goto(VERCEL_URL, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)  # API 요청 완료 대기
        
        if requests:
            print("API 요청 분석:")
            for req in requests:
                if 'duration' in req:
                    endpoint = req['url'].replace(VERCEL_URL, '').split('?')[0]
                    print(f"  - {req['method']} {endpoint}: {req['duration']:.3f}초 (상태: {req['status']})")
        
        await browser.close()
        
        print("\n📊 측정 완료")
        print("스크린샷 저장됨: vercel_dashboard.png, vercel_customers.png")

async def main():
    print("🚀 Vercel 실제 사용자 경험 측정")
    print(f"URL: {VERCEL_URL}")
    print("=" * 60)
    
    await measure_real_loading_time()
    
    print("\n💡 참고:")
    print("- DOM 로드 시간: HTML과 기본 구조가 로드되는 시간")
    print("- 콘텐츠 표시 시간: 사용자가 실제로 콘텐츠를 볼 수 있는 시간")
    print("- 실제 체감 속도는 인터넷 연결 상태에 따라 달라질 수 있습니다")

if __name__ == "__main__":
    asyncio.run(main())