#!/usr/bin/env python3
"""
전체 시스템 상태를 완전히 진단
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright

async def check_full_system():
    print("🔍 AIBIO Center 전체 시스템 진단")
    print("=" * 60)
    
    # 1. 백엔드 API 체크
    print("\n1️⃣ Backend API (Railway)")
    backend_url = "https://center-production-1421.up.railway.app"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Health check
            async with session.get(f"{backend_url}/health") as resp:
                print(f"   /health: {resp.status} ✅")
                
            # API docs
            async with session.get(f"{backend_url}/docs") as resp:
                print(f"   /docs: {resp.status} ✅")
                
            # Test auth endpoint
            async with session.post(
                f"{backend_url}/api/v1/auth/login",
                json={"email": "admin@aibio.com", "password": "admin123"}
            ) as resp:
                print(f"   /api/v1/auth/login: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   → Login successful! Token: {data.get('access_token', '')[:20]}...")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 2. 프론트엔드 체크
    print("\n2️⃣ Frontend (Vercel)")
    frontend_url = "https://center-ten.vercel.app"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 콘솔 메시지 수집
        console_logs = []
        errors = []
        api_calls = []
        
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("request", lambda req: api_calls.append(req.url) if 'api' in req.url or 'railway' in req.url else None)
        
        try:
            # 메인 페이지 로드
            response = await page.goto(frontend_url, wait_until="networkidle")
            print(f"   Main page: {response.status} ✅")
            
            await page.wait_for_timeout(3000)
            
            # 현재 URL 확인
            current_url = page.url
            print(f"   Redirected to: {current_url}")
            
            # 페이지 스크린샷
            # await page.screenshot(path="vercel_page.png")
            # print("   Screenshot saved: vercel_page.png")
            
            # 로그인 시도
            if "/login" in current_url:
                print("\n   🔐 Attempting login...")
                
                # 이메일 입력
                email_input = await page.locator('input[type="email"], input[name="email"], input[placeholder*="이메일"]').first
                if email_input:
                    await email_input.fill("admin@aibio.com")
                    print("   ✅ Email entered")
                
                # 비밀번호 입력
                password_input = await page.locator('input[type="password"], input[name="password"]').first
                if password_input:
                    await password_input.fill("admin123")
                    print("   ✅ Password entered")
                
                # 로그인 버튼 클릭
                login_button = await page.locator('button[type="submit"], button:has-text("로그인")').first
                if login_button:
                    await login_button.click()
                    print("   ✅ Login button clicked")
                    
                    # 응답 대기
                    await page.wait_for_timeout(3000)
                    
                    # 로그인 후 URL
                    after_login_url = page.url
                    print(f"   After login URL: {after_login_url}")
            
            # 콘솔 로그 확인
            if console_logs:
                print("\n   📋 Console logs:")
                for log in console_logs[:5]:
                    print(f"      {log}")
                    
            if errors:
                print("\n   ❌ Page errors:")
                for err in errors:
                    print(f"      {err}")
                    
            if api_calls:
                print("\n   🌐 API calls made:")
                for call in set(api_calls):
                    print(f"      {call}")
            else:
                print("\n   ⚠️  No API calls detected!")
                
            # localStorage 확인
            storage_data = await page.evaluate("""() => {
                return {
                    localStorage: Object.keys(localStorage),
                    sessionStorage: Object.keys(sessionStorage),
                    cookies: document.cookie
                }
            }""")
            print(f"\n   💾 Storage:")
            print(f"      localStorage: {storage_data['localStorage']}")
            print(f"      sessionStorage: {storage_data['sessionStorage']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        await browser.close()
    
    # 3. 진단 결과
    print("\n" + "=" * 60)
    print("📊 진단 결과:")
    print("\n가능한 문제들:")
    print("1. CORS 설정 문제 - 백엔드가 Vercel 도메인을 허용하지 않음")
    print("2. 프론트엔드 빌드 시 환경변수가 적용되지 않음")
    print("3. 프론트엔드 코드에서 API URL을 하드코딩했을 가능성")
    print("4. Authentication 관련 이슈")

if __name__ == "__main__":
    asyncio.run(check_full_system())