#!/usr/bin/env python3
"""
실제 사용자가 경험하는 로딩 문제 분석
"""
import asyncio
import time
from playwright.async_api import async_playwright

VERCEL_URL = "https://center-ten.vercel.app"

async def analyze_loading_issue():
    """실제 로딩 문제 상세 분석"""
    async with async_playwright() as p:
        # 실제 브라우저로 확인
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100  # 천천히 동작
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        # 개발자 도구 활성화
        page = await context.new_page()
        
        print("🔍 실제 로딩 문제 분석")
        print("=" * 60)
        
        # 모든 네트워크 요청 추적
        requests = []
        slow_requests = []
        
        async def handle_request(request):
            requests.append({
                'url': request.url,
                'method': request.method,
                'type': request.resource_type,
                'start': time.time()
            })
        
        async def handle_response(response):
            for req in requests:
                if req['url'] == response.url and 'end' not in req:
                    req['end'] = time.time()
                    req['duration'] = (req['end'] - req['start']) * 1000
                    req['status'] = response.status
                    
                    # 500ms 이상 걸린 요청 추적
                    if req['duration'] > 500:
                        slow_requests.append(req)
                    break
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # 콘솔 메시지 추적
        console_errors = []
        page.on('console', lambda msg: console_errors.append(msg) if msg.type == 'error' else None)
        
        print("\n1️⃣ 로그인 페이지 로딩...")
        start_time = time.time()
        
        await page.goto(VERCEL_URL)
        
        # 로그인 폼이 나타날 때까지 시간 측정
        await page.wait_for_selector('form', timeout=30000)
        login_page_time = time.time() - start_time
        print(f"✅ 로그인 페이지 로드: {login_page_time:.2f}초")
        
        # 로그인
        print("\n2️⃣ 로그인 진행...")
        await page.fill('input[type="email"]', 'admin@example.com')
        await page.fill('input[type="password"]', 'admin123')
        
        # 로그인 버튼 클릭 전 준비
        login_start = time.time()
        
        # Promise를 사용하여 네비게이션 대기
        await page.click('button[type="submit"]')
        
        print("\n3️⃣ 대시보드 로딩 대기...")
        
        # 여러 단계로 나누어 측정
        stages = []
        
        # Stage 1: 페이지 네비게이션
        try:
            await page.wait_for_url("**/", timeout=10000)
            nav_time = time.time() - login_start
            stages.append(('네비게이션', nav_time))
            print(f"  - 네비게이션 완료: {nav_time:.2f}초")
        except:
            print("  - 네비게이션 타임아웃")
        
        # Stage 2: DOM 로드
        try:
            await page.wait_for_load_state('domcontentloaded')
            dom_time = time.time() - login_start
            stages.append(('DOM 로드', dom_time))
            print(f"  - DOM 로드 완료: {dom_time:.2f}초")
        except:
            print("  - DOM 로드 타임아웃")
        
        # Stage 3: 첫 번째 콘텐츠 표시
        try:
            await page.wait_for_selector('div', timeout=10000)
            first_content_time = time.time() - login_start
            stages.append(('첫 콘텐츠', first_content_time))
            print(f"  - 첫 콘텐츠 표시: {first_content_time:.2f}초")
        except:
            print("  - 첫 콘텐츠 타임아웃")
        
        # Stage 4: 통계 카드 표시
        try:
            await page.wait_for_selector('.grid', timeout=10000)
            stats_time = time.time() - login_start
            stages.append(('통계 카드', stats_time))
            print(f"  - 통계 카드 표시: {stats_time:.2f}초")
        except:
            print("  - 통계 카드 타임아웃")
        
        total_time = time.time() - login_start
        print(f"\n🏁 총 대시보드 로딩 시간: {total_time:.2f}초")
        
        # 느린 요청 분석
        if slow_requests:
            print(f"\n⚠️ 느린 요청 ({len(slow_requests)}개):")
            for req in sorted(slow_requests, key=lambda x: x['duration'], reverse=True)[:10]:
                url = req['url'].replace(VERCEL_URL, '')
                if len(url) > 60:
                    url = url[:60] + '...'
                print(f"  - {url}")
                print(f"    시간: {req['duration']:.0f}ms, 타입: {req['type']}")
        
        # API 요청 분석
        api_requests = [r for r in requests if '/api/' in r['url'] and 'duration' in r]
        if api_requests:
            print(f"\n📡 API 요청 분석:")
            total_api_time = sum(r['duration'] for r in api_requests)
            print(f"  - 총 API 요청: {len(api_requests)}개")
            print(f"  - 총 API 시간: {total_api_time:.0f}ms")
            
            for req in sorted(api_requests, key=lambda x: x['duration'], reverse=True)[:5]:
                endpoint = req['url'].split('/api/')[1].split('?')[0]
                print(f"  - {endpoint}: {req['duration']:.0f}ms")
        
        # JavaScript 에러 확인
        if console_errors:
            print(f"\n❌ JavaScript 에러 ({len(console_errors)}개):")
            for error in console_errors[:5]:
                print(f"  - {error.text[:100]}...")
        
        # 스크린샷
        await page.screenshot(path='loading_issue_final.png')
        print(f"\n📸 최종 스크린샷: loading_issue_final.png")
        
        # 문제 진단
        print(f"\n🔍 문제 진단:")
        print("=" * 60)
        
        if total_time > 4:
            print("❌ 로딩 시간이 여전히 느립니다.")
            
            # 가능한 원인 분석
            if total_api_time > 2000:
                print("  → API 응답이 느립니다 (2초 이상)")
            
            if len(slow_requests) > 5:
                print("  → 많은 리소스가 느리게 로드됩니다")
            
            if console_errors:
                print("  → JavaScript 에러가 발생했습니다")
            
            # 단계별 지연 분석
            if stages:
                prev_time = 0
                print("\n  단계별 지연:")
                for stage, stage_time in stages:
                    delay = stage_time - prev_time
                    if delay > 1:
                        print(f"    - {stage}: +{delay:.2f}초 ⚠️")
                    else:
                        print(f"    - {stage}: +{delay:.2f}초")
                    prev_time = stage_time
        
        input("\n분석 완료. Enter를 눌러 브라우저를 닫으세요...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_loading_issue())