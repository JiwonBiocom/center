#!/usr/bin/env python3
"""
올바른 계정으로 실제 로딩 성능 측정
"""
import asyncio
import time
from playwright.async_api import async_playwright
from datetime import datetime

VERCEL_URL = "https://center-ten.vercel.app"

async def test_real_performance():
    """올바른 계정으로 실제 성능 측정"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print("🚀 올바른 계정으로 실제 성능 측정")
        print(f"URL: {VERCEL_URL}")
        print(f"계정: admin@aibio.kr")
        print(f"시간: {datetime.now()}")
        print("=" * 60)
        
        # 네트워크 요청 추적
        api_requests = []
        js_chunks = []
        
        async def handle_response(response):
            if '/api/' in response.url:
                start_time = getattr(response.request, 'start_time', 0)
                api_requests.append({
                    'url': response.url.split('/api/')[1].split('?')[0],
                    'status': response.status,
                    'duration': (time.time() - start_time) * 1000 if start_time else 0
                })
            elif response.url.endswith('.js'):
                js_chunks.append({
                    'name': response.url.split('/')[-1],
                    'size': len(await response.body()) if response.ok else 0
                })
        
        page.on('response', handle_response)
        
        # 1. 로그인 페이지 로딩
        print("\n📱 1단계: 로그인 페이지 접속")
        start_time = time.time()
        
        await page.goto(VERCEL_URL)
        await page.wait_for_selector('form')
        
        login_page_time = time.time() - start_time
        print(f"✅ 로그인 페이지: {login_page_time:.2f}초")
        
        # 로드된 JavaScript 청크 표시
        initial_js_size = sum(chunk['size'] for chunk in js_chunks)
        print(f"📦 초기 JS 크기: {initial_js_size / 1024:.1f}KB ({len(js_chunks)}개 파일)")
        
        # 2. 로그인 진행
        print(f"\n🔐 2단계: 로그인 진행")
        await page.fill('input[type="email"]', 'admin@aibio.kr')
        await page.fill('input[type="password"]', 'admin123')
        
        # 로그인 버튼 클릭 및 대시보드 로딩 측정
        dashboard_start = time.time()
        
        # 요청에 시작 시간 추가
        async def add_start_time(request):
            setattr(request, 'start_time', time.time())
        
        page.on('request', add_start_time)
        
        await page.click('button[type="submit"]')
        
        print("⏳ 대시보드 로딩 중...")
        
        # 단계별 로딩 측정
        stages = []
        
        try:
            # Stage 1: URL 변경 (리다이렉션)
            await page.wait_for_url("**/", timeout=15000)
            nav_time = time.time() - dashboard_start
            stages.append(('리다이렉션', nav_time))
            print(f"  ✓ 리다이렉션: {nav_time:.2f}초")
        except:
            print("  ✗ 리다이렉션 타임아웃")
        
        try:
            # Stage 2: 첫 번째 헤더 요소 표시
            await page.wait_for_selector('header', timeout=10000)
            header_time = time.time() - dashboard_start
            stages.append(('헤더 표시', header_time))
            print(f"  ✓ 헤더 표시: {header_time:.2f}초")
        except:
            print("  ✗ 헤더 표시 타임아웃")
        
        try:
            # Stage 3: 메인 콘텐츠 표시
            await page.wait_for_selector('main', timeout=10000)
            main_time = time.time() - dashboard_start
            stages.append(('메인 콘텐츠', main_time))
            print(f"  ✓ 메인 콘텐츠: {main_time:.2f}초")
        except:
            print("  ✗ 메인 콘텐츠 타임아웃")
        
        try:
            # Stage 4: 통계 카드 표시
            await page.wait_for_selector('.grid', timeout=15000)
            stats_time = time.time() - dashboard_start
            stages.append(('통계 카드', stats_time))
            print(f"  ✓ 통계 카드: {stats_time:.2f}초")
        except:
            print("  ✗ 통계 카드 타임아웃")
        
        try:
            # Stage 5: 로딩 스피너 사라짐 (완전한 로딩)
            await page.wait_for_selector('.animate-spin', state='detached', timeout=10000)
            complete_time = time.time() - dashboard_start
            stages.append(('완전 로딩', complete_time))
            print(f"  ✓ 완전 로딩: {complete_time:.2f}초")
        except:
            print("  ✗ 로딩 스피너가 남아있음")
        
        total_dashboard_time = time.time() - dashboard_start
        print(f"\n🏁 대시보드 총 로딩 시간: {total_dashboard_time:.2f}초")
        
        # 3. API 요청 분석
        if api_requests:
            print(f"\n📡 API 요청 분석:")
            print("-" * 60)
            
            total_api_time = sum(req['duration'] for req in api_requests if req['duration'] > 0)
            print(f"총 API 요청: {len(api_requests)}개")
            print(f"총 API 시간: {total_api_time:.0f}ms")
            
            # 느린 API 요청 표시
            slow_apis = [req for req in api_requests if req['duration'] > 500]
            if slow_apis:
                print(f"\n⚠️ 느린 API 요청 (500ms 이상):")
                for req in sorted(slow_apis, key=lambda x: x['duration'], reverse=True):
                    status_icon = "✅" if req['status'] == 200 else "❌"
                    print(f"  {status_icon} {req['url']:30} {req['duration']:6.0f}ms ({req['status']})")
            
            # 모든 API 요청 표시
            print(f"\n📊 모든 API 요청:")
            for req in api_requests:
                status_icon = "✅" if req['status'] == 200 else "❌"
                print(f"  {status_icon} {req['url']:30} {req['duration']:6.0f}ms ({req['status']})")
        
        # 4. 추가 로드된 JavaScript 분석
        additional_js = js_chunks[len([c for c in js_chunks if 'initial' in str(c)]):]
        if additional_js:
            additional_size = sum(chunk['size'] for chunk in additional_js)
            print(f"\n📥 추가 로드된 JavaScript:")
            print(f"크기: {additional_size / 1024:.1f}KB ({len(additional_js)}개 파일)")
            for chunk in additional_js[:5]:
                print(f"  - {chunk['name']}: {chunk['size'] / 1024:.1f}KB")
        
        # 5. 성능 분석 및 개선점
        print(f"\n📊 성능 분석:")
        print("=" * 60)
        
        if total_dashboard_time <= 2:
            print("⚡ 매우 빠름 (2초 이하)")
        elif total_dashboard_time <= 3:
            print("✅ 빠름 (3초 이하)")
        elif total_dashboard_time <= 5:
            print("🔶 보통 (5초 이하)")
        else:
            print("❌ 느림 (5초 초과)")
        
        # 병목 지점 분석
        print(f"\n🔍 병목 지점 분석:")
        if total_api_time > 2000:
            print(f"  ⚠️ API 응답이 매우 느림 ({total_api_time:.0f}ms)")
        
        if any(req['duration'] > 1000 for req in api_requests):
            print("  ⚠️ 1초 이상 걸리는 API가 있음")
        
        if total_dashboard_time > 3 and total_api_time < 1000:
            print("  ⚠️ API는 빠르지만 프론트엔드 렌더링이 느림")
        
        # 개선 제안
        print(f"\n💡 개선 제안:")
        if total_api_time > 1000:
            print("  1. API 서버 성능 최적화 (쿼리 튜닝)")
            print("  2. API 응답 캐싱 도입")
        
        if len(api_requests) > 5:
            print("  3. API 요청 수 줄이기 (데이터 통합)")
        
        if total_dashboard_time > 3:
            print("  4. 로딩 UX 개선 (스켈레톤 스크린)")
            print("  5. 중요하지 않은 데이터는 지연 로딩")
        
        # 스크린샷
        await page.screenshot(path='real_performance_test.png')
        print(f"\n📸 스크린샷: real_performance_test.png")
        
        input("\n측정 완료. Enter를 눌러 브라우저를 닫으세요...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_real_performance())