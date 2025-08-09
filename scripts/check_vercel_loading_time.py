#!/usr/bin/env python3
"""
Vercel 배포 서버 로딩 시간 측정
"""
import time
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

VERCEL_URL = "https://center-ten.vercel.app"

async def measure_page_loading(page_name, url, wait_selector):
    """특정 페이지의 로딩 시간 측정"""
    print(f"\n🔍 {page_name} 로딩 측정 중...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # 네트워크 요청 추적
        api_requests = []
        
        async def handle_request(request):
            if '/api/' in request.url:
                api_requests.append({
                    'url': request.url,
                    'start': time.time(),
                    'method': request.method
                })
        
        async def handle_response(response):
            for req in api_requests:
                if req['url'] == response.url and 'end' not in req:
                    req['end'] = time.time()
                    req['duration'] = req['end'] - req['start']
                    req['status'] = response.status
                    req['size'] = len(await response.body()) if response.status == 200 else 0
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # 콘솔 메시지 추적
        console_messages = []
        page.on('console', lambda msg: console_messages.append({'type': msg.type, 'text': msg.text}))
        
        try:
            # 페이지 로딩 시작
            start_time = time.time()
            
            # 페이지로 이동
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 특정 요소가 로드될 때까지 대기
            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=10000)
            
            # 추가 대기 (동적 콘텐츠 로딩)
            await page.wait_for_timeout(1000)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n📊 {page_name} 로딩 결과:")
            print(f"총 로딩 시간: {total_time:.2f}초")
            
            # 성능 평가
            if total_time < 1.5:
                evaluation = "⚡ 매우 빠름 (1.5초 미만)"
            elif total_time < 3.0:
                evaluation = "✅ 빠름 (3초 미만)"
            elif total_time < 5.0:
                evaluation = "🔶 보통 (5초 미만)"
            elif total_time < 8.0:
                evaluation = "⚠️ 느림 (8초 미만)"
            else:
                evaluation = "❌ 매우 느림 (8초 이상)"
            
            print(f"평가: {evaluation}")
            
            # API 요청 분석
            if api_requests:
                print(f"\n🌐 API 요청 분석:")
                total_api_time = 0
                for req in api_requests:
                    if 'duration' in req:
                        endpoint = req['url'].replace(VERCEL_URL, '').split('?')[0]
                        print(f"  - {req['method']} {endpoint}: {req['duration']:.3f}초 (상태: {req['status']})")
                        total_api_time += req['duration']
                
                if total_api_time > 0:
                    print(f"  총 API 시간: {total_api_time:.3f}초")
            
            # 렌더링 성능
            render_time = total_time - (total_api_time if api_requests else 0)
            print(f"\n⚡ 렌더링 시간 (추정): {render_time:.3f}초")
            
            # 페이지별 특수 정보
            if page_name == "대시보드":
                # 통계 카드 개수 확인
                stat_cards = await page.query_selector_all('.grid > div[class*="bg-white"]')
                print(f"\n📈 대시보드 정보:")
                print(f"  - 통계 카드: {len(stat_cards)}개")
                
            elif page_name == "고객 관리":
                # 테이블 행 개수 확인
                table_rows = await page.query_selector_all('tbody tr')
                print(f"\n👥 고객 관리 정보:")
                print(f"  - 표시된 고객: {len(table_rows)}명")
            
            # 에러 확인
            errors = [msg for msg in console_messages if msg['type'] == 'error']
            if errors:
                print(f"\n⚠️ 콘솔 에러 발견: {len(errors)}개")
                for error in errors[:3]:  # 최대 3개만 표시
                    print(f"  - {error['text'][:100]}...")
            
            # 스크린샷 저장
            screenshot_name = f"{page_name.replace(' ', '_')}_loaded_{int(time.time())}.png"
            await page.screenshot(path=screenshot_name)
            print(f"\n📸 스크린샷 저장: {screenshot_name}")
            
            return total_time, evaluation
            
        except Exception as e:
            print(f"❌ {page_name} 로딩 실패: {e}")
            return None, "실패"
        
        finally:
            await browser.close()

async def main():
    print(f"🚀 Vercel 배포 서버 성능 측정")
    print(f"URL: {VERCEL_URL}")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 대시보드 측정
    dashboard_time, dashboard_eval = await measure_page_loading(
        "대시보드", 
        VERCEL_URL + "/", 
        ".grid"  # 통계 그리드가 로드될 때까지 대기
    )
    
    # 2. 고객 관리 측정
    customers_time, customers_eval = await measure_page_loading(
        "고객 관리",
        VERCEL_URL + "/customers",
        "table"  # 테이블이 로드될 때까지 대기
    )
    
    # 요약
    print("\n" + "=" * 60)
    print("📊 측정 요약:")
    print(f"\n1. 대시보드:")
    if dashboard_time:
        print(f"   - 로딩 시간: {dashboard_time:.2f}초")
        print(f"   - 평가: {dashboard_eval}")
    else:
        print("   - 측정 실패")
    
    print(f"\n2. 고객 관리:")
    if customers_time:
        print(f"   - 로딩 시간: {customers_time:.2f}초")
        print(f"   - 평가: {customers_eval}")
    else:
        print("   - 측정 실패")
    
    if dashboard_time and customers_time:
        print(f"\n🔍 비교:")
        diff = abs(customers_time - dashboard_time)
        faster = "대시보드" if dashboard_time < customers_time else "고객 관리"
        print(f"   - {faster} 페이지가 {diff:.2f}초 더 빠름")
    
    print("\n✅ 측정 완료")

if __name__ == "__main__":
    asyncio.run(main())