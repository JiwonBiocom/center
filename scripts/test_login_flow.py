#!/usr/bin/env python3
"""
실제 로그인 플로우 테스트
"""

import asyncio
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 콘솔 메시지 수집
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        
        print("🔍 AIBIO 센터 관리 시스템 로그인 테스트")
        print("=" * 60)
        
        try:
            # 1. 메인 페이지 접속
            print("\n1️⃣ 사이트 접속...")
            await page.goto("https://center-ten.vercel.app", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            current_url = page.url
            print(f"   현재 URL: {current_url}")
            
            # 2. 로그인 페이지 확인
            if "/login" in current_url:
                print("   ✅ 로그인 페이지로 리다이렉트됨")
                
                # 3. 로그인 폼 찾기
                print("\n2️⃣ 로그인 시도...")
                
                # 이메일 입력
                email_input = page.locator('input[type="email"], input[placeholder*="이메일"], input[name="email"]').first
                if await email_input.is_visible():
                    await email_input.fill("admin@aibio.com")
                    print("   ✅ 이메일 입력: admin@aibio.com")
                else:
                    print("   ❌ 이메일 입력 필드를 찾을 수 없음")
                
                # 비밀번호 입력
                password_input = page.locator('input[type="password"], input[placeholder*="비밀번호"], input[name="password"]').first
                if await password_input.is_visible():
                    await password_input.fill("admin123")
                    print("   ✅ 비밀번호 입력: ********")
                else:
                    print("   ❌ 비밀번호 입력 필드를 찾을 수 없음")
                
                # 스크린샷 (디버깅용)
                await page.screenshot(path="login_form.png")
                print("   📸 스크린샷 저장: login_form.png")
                
                # 로그인 버튼 클릭
                login_button = page.locator('button[type="submit"], button:text("로그인"), button:text("Login")').first
                if await login_button.is_visible():
                    print("   🔘 로그인 버튼 클릭...")
                    await login_button.click()
                    
                    # 응답 대기
                    await page.wait_for_timeout(3000)
                    
                    # 4. 로그인 결과 확인
                    print("\n3️⃣ 로그인 결과...")
                    after_url = page.url
                    print(f"   로그인 후 URL: {after_url}")
                    
                    if "/dashboard" in after_url or "/login" not in after_url:
                        print("   ✅ 로그인 성공! 대시보드로 이동")
                        
                        # 대시보드 스크린샷
                        await page.screenshot(path="dashboard.png")
                        print("   📸 대시보드 스크린샷: dashboard.png")
                        
                        # 페이지 제목 확인
                        title = await page.title()
                        print(f"   📄 페이지 제목: {title}")
                        
                        # 주요 요소 확인
                        sidebar = await page.locator('nav, aside, .sidebar').count()
                        if sidebar > 0:
                            print("   ✅ 사이드바 메뉴 발견")
                        
                        # API 호출 확인
                        await page.wait_for_timeout(2000)
                        
                    else:
                        print("   ❌ 로그인 실패 - 여전히 로그인 페이지")
                        
                        # 에러 메시지 확인
                        error_msg = await page.locator('.error, .alert, [role="alert"]').text_content()
                        if error_msg:
                            print(f"   에러 메시지: {error_msg}")
                else:
                    print("   ❌ 로그인 버튼을 찾을 수 없음")
            
            # 5. 콘솔 메시지 확인
            if console_messages:
                print("\n4️⃣ 콘솔 메시지:")
                for msg in console_messages[:10]:  # 처음 10개만
                    print(f"   {msg}")
            
        except Exception as e:
            print(f"\n❌ 테스트 중 오류 발생: {e}")
            await page.screenshot(path="error.png")
            print("   📸 오류 스크린샷: error.png")
        
        await browser.close()
        
        print("\n" + "=" * 60)
        print("테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_login())