#!/usr/bin/env python3
"""
실제 사용자가 체감하는 로딩 시간 측정
"""
import asyncio
import time
from playwright.async_api import async_playwright
from datetime import datetime

VERCEL_URL = "https://center-ten.vercel.app"

async def measure_full_page_load():
    """전체 페이지 로딩 시간 측정 (JavaScript 실행 포함)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # 실제 브라우저로 확인
            slow_mo=100  # 동작을 천천히 볼 수 있게
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        # 성능 측정을 위한 이벤트 추적
        events = []
        
        # 콘솔 메시지 추적
        console_logs = []
        page.on('console', lambda msg: console_logs.append({
            'time': time.time(),
            'type': msg.type,
            'text': msg.text
        }))
        
        # 네트워크 요청 추적
        network_requests = []
        
        async def handle_request(request):
            network_requests.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type,
                'start_time': time.time()
            })
        
        async def handle_response(response):
            for req in network_requests:
                if req['url'] == response.url and 'end_time' not in req:
                    req['end_time'] = time.time()
                    req['duration'] = (req['end_time'] - req['start_time']) * 1000  # ms
                    req['status'] = response.status
                    req['size'] = len(await response.body()) if response.ok else 0
                    break
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        print("🚀 대시보드 전체 로딩 시간 측정")
        print("=" * 60)
        
        # 측정 시작
        start_time = time.time()
        events.append(('start', 0))
        
        try:
            # 페이지 로드
            print("📱 페이지 이동 중...")
            await page.goto(VERCEL_URL, wait_until='commit')
            navigation_time = time.time() - start_time
            events.append(('navigation', navigation_time))
            print(f"✓ 네비게이션 완료: {navigation_time:.2f}초")
            
            # DOM 로드 대기
            await page.wait_for_load_state('domcontentloaded')
            dom_time = time.time() - start_time
            events.append(('domcontentloaded', dom_time))
            print(f"✓ DOM 로드 완료: {dom_time:.2f}초")
            
            # 네트워크 유휴 상태 대기 (모든 리소스 로드)
            await page.wait_for_load_state('networkidle')
            network_idle_time = time.time() - start_time
            events.append(('networkidle', network_idle_time))
            print(f"✓ 네트워크 유휴: {network_idle_time:.2f}초")
            
            # 주요 콘텐츠 표시 대기
            print("\n⏳ 콘텐츠 로딩 대기 중...")
            
            # 통계 카드가 표시될 때까지 대기
            try:
                await page.wait_for_selector('.grid > div', timeout=10000)
                stats_visible_time = time.time() - start_time
                events.append(('stats_visible', stats_visible_time))
                print(f"✓ 통계 카드 표시: {stats_visible_time:.2f}초")
                
                # 통계 카드 개수 확인
                stat_cards = await page.query_selector_all('.grid > div')
                print(f"  - 통계 카드 개수: {len(stat_cards)}개")
            except:
                print("⚠️ 통계 카드를 찾을 수 없음")
            
            # 차트가 있다면 차트 로딩 대기
            try:
                await page.wait_for_selector('canvas', timeout=3000)
                chart_visible_time = time.time() - start_time
                events.append(('chart_visible', chart_visible_time))
                print(f"✓ 차트 표시: {chart_visible_time:.2f}초")
            except:
                print("  - 차트 없음 또는 로드 실패")
            
            # 최종 스크린샷
            total_time = time.time() - start_time
            await page.screenshot(path='dashboard_loaded.png')
            print(f"\n📸 스크린샷 저장: dashboard_loaded.png")
            
            # 결과 분석
            print(f"\n📊 로딩 시간 분석")
            print("=" * 60)
            print(f"🏁 전체 로딩 시간: {total_time:.2f}초")
            
            # 단계별 시간 분석
            print(f"\n⏱️ 단계별 소요 시간:")
            prev_time = 0
            for event_name, event_time in events:
                if event_name != 'start':
                    step_duration = event_time - prev_time
                    print(f"  - {event_name}: {step_duration:.2f}초 (누적: {event_time:.2f}초)")
                    prev_time = event_time
            
            # 네트워크 요청 분석
            print(f"\n🌐 네트워크 요청 분석:")
            
            # 리소스 타입별 분류
            by_type = {}
            total_size = 0
            for req in network_requests:
                if 'duration' in req:
                    resource_type = req['resource_type']
                    if resource_type not in by_type:
                        by_type[resource_type] = {'count': 0, 'total_time': 0, 'total_size': 0}
                    by_type[resource_type]['count'] += 1
                    by_type[resource_type]['total_time'] += req['duration']
                    by_type[resource_type]['total_size'] += req.get('size', 0)
                    total_size += req.get('size', 0)
            
            for resource_type, stats in by_type.items():
                avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
                print(f"  - {resource_type}: {stats['count']}개, 평균 {avg_time:.0f}ms, 총 {stats['total_size']/1024:.1f}KB")
            
            print(f"  - 전체 다운로드 크기: {total_size/1024:.1f}KB")
            
            # 느린 요청 찾기
            slow_requests = [req for req in network_requests if req.get('duration', 0) > 500]
            if slow_requests:
                print(f"\n⚠️ 느린 요청 (500ms 이상):")
                for req in sorted(slow_requests, key=lambda x: x['duration'], reverse=True)[:5]:
                    url = req['url'].replace(VERCEL_URL, '')
                    print(f"  - {url}: {req['duration']:.0f}ms")
            
            # JavaScript 에러 확인
            js_errors = [log for log in console_logs if log['type'] == 'error']
            if js_errors:
                print(f"\n❌ JavaScript 에러: {len(js_errors)}개")
                for error in js_errors[:3]:
                    print(f"  - {error['text'][:100]}...")
            
            # 성능 평가
            print(f"\n💡 성능 평가:")
            if total_time < 2:
                print("⚡ 빠름 (2초 미만)")
            elif total_time < 3:
                print("✅ 양호 (3초 미만)")
            elif total_time < 5:
                print("🔶 보통 (5초 미만)")
            else:
                print("❌ 느림 (5초 이상)")
                print("\n🔍 성능 개선 제안:")
                print("  1. 번들 크기 최적화 (코드 스플리팅)")
                print("  2. 이미지 최적화 및 레이지 로딩")
                print("  3. API 요청 병렬화 또는 캐싱")
                print("  4. 불필요한 JavaScript 제거")
                print("  5. 서버 사이드 렌더링 (SSR) 고려")
            
        except Exception as e:
            print(f"\n❌ 측정 실패: {e}")
        
        input("\n브라우저를 닫으려면 Enter를 누르세요...")
        await browser.close()

async def main():
    await measure_full_page_load()

if __name__ == "__main__":
    asyncio.run(main())