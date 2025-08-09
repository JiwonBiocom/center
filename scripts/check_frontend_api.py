#!/usr/bin/env python3
"""
프론트엔드의 API 호출 패턴 확인
"""

import asyncio
from playwright.async_api import async_playwright

async def check_api_calls():
    """프론트엔드가 호출하는 API 확인"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 네트워크 요청 추적
        api_calls = []
        
        def log_request(request):
            if 'api' in request.url or request.url.endswith('.json'):
                api_calls.append({
                    'url': request.url,
                    'method': request.method,
                    'status': None
                })
        
        def log_response(response):
            for call in api_calls:
                if call['url'] == response.url:
                    call['status'] = response.status
                    call['ok'] = response.ok
        
        page.on("request", log_request)
        page.on("response", log_response)
        
        url = "https://center-production-1421.up.railway.app"
        print(f"🔍 Monitoring API calls for: {url}")
        print("=" * 60)
        
        try:
            # 페이지 로드
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # 로그인 페이지인지 확인
            title = await page.title()
            print(f"\n📄 Page Title: {title}")
            
            # 페이지 내용 확인
            body_text = await page.evaluate("document.body.innerText")
            if "로그인" in body_text or "login" in body_text.lower():
                print("🔐 Login page detected")
                
                # 로그인 폼 찾기
                if await page.locator('input[type="email"], input[type="text"]').count() > 0:
                    print("📝 Login form found")
            
            # API 호출 결과
            print(f"\n🌐 API Calls Made:")
            if api_calls:
                for call in api_calls:
                    status_icon = "✅" if call.get('ok') else "❌"
                    print(f"   {status_icon} {call['method']} {call['url']}")
                    if 'status' in call and call['status']:
                        print(f"      Status: {call['status']}")
            else:
                print("   No API calls detected")
            
            # 콘솔 메시지 확인
            console_msgs = []
            page.on("console", lambda msg: console_msgs.append(msg))
            
            # 특정 경로 테스트
            test_paths = ['/login', '/dashboard', '/customers']
            for path in test_paths:
                try:
                    print(f"\n🔄 Testing path: {path}")
                    await page.goto(f"{url}{path}", wait_until="domcontentloaded")
                    await page.wait_for_timeout(1000)
                    
                    # 현재 URL 확인
                    current = page.url
                    print(f"   Current URL: {current}")
                except Exception as e:
                    print(f"   Error: {e}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        await browser.close()
        
        # 분석 결과
        print("\n" + "=" * 60)
        print("📊 Analysis Summary:")
        
        failed_calls = [c for c in api_calls if not c.get('ok')]
        if failed_calls:
            print(f"\n❌ Failed API calls: {len(failed_calls)}")
            for call in failed_calls[:5]:
                print(f"   - {call['url']} (Status: {call.get('status', 'Unknown')})")
        
        # 권장사항
        print("\n💡 Recommendations:")
        if any('api/v1' in c['url'] for c in api_calls):
            print("   - Frontend is trying to call /api/v1/* endpoints")
            print("   - Backend might not have these routes configured")
        else:
            print("   - Frontend might be in static mode (no API calls)")
            print("   - Check if environment variables are set correctly")

if __name__ == "__main__":
    asyncio.run(check_api_calls())