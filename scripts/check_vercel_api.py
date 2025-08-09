#!/usr/bin/env python3
"""
Vercel 배포 사이트의 API 호출 확인
"""

import asyncio
from playwright.async_api import async_playwright

async def check_vercel_api():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 네트워크 요청 추적
        api_calls = []
        
        def log_request(request):
            if 'api' in request.url or 'railway' in request.url:
                print(f"🌐 API Call: {request.method} {request.url}")
                api_calls.append(request.url)
        
        page.on("request", log_request)
        
        url = "https://center-ten.vercel.app"
        print(f"🔍 Checking Vercel deployment: {url}")
        print("=" * 60)
        
        try:
            # 페이지 로드
            response = await page.goto(url, wait_until="networkidle")
            print(f"✅ Page loaded: {response.status}")
            
            # 로그인 페이지 확인
            await page.wait_for_timeout(2000)
            
            # 페이지 내용 확인
            title = await page.title()
            print(f"📄 Page title: {title}")
            
            # 로그인 폼 확인
            login_form = await page.locator('input[type="email"], input[type="password"]').count()
            if login_form > 0:
                print("🔐 Login form detected!")
                
                # 환경 변수 확인을 위한 네트워크 탭 체크
                print("\n📊 API Configuration:")
                if len(api_calls) > 0:
                    print(f"   ✅ API URL configured: {api_calls[0]}")
                else:
                    print("   ⚠️  No API calls detected - checking localStorage...")
                    
                    # localStorage 확인
                    storage = await page.evaluate("() => Object.keys(localStorage)")
                    print(f"   localStorage keys: {storage}")
            
            # 특정 경로 테스트
            print("\n🔄 Testing login flow...")
            await page.goto(f"{url}/login")
            await page.wait_for_timeout(1000)
            
            # 현재 URL 확인
            current_url = page.url
            print(f"   Current URL: {current_url}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        await browser.close()
        
        # 결과 분석
        print("\n" + "=" * 60)
        if api_calls:
            print("✅ Frontend is configured to call backend API")
            for call in set(api_calls):
                print(f"   - {call}")
        else:
            print("⚠️  No API calls detected. Check VITE_API_URL in Vercel settings.")

if __name__ == "__main__":
    asyncio.run(check_vercel_api())