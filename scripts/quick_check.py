#!/usr/bin/env python3
"""
빠른 웹 애플리케이션 체크
"""

import asyncio
from playwright.async_api import async_playwright

async def quick_check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 콘솔 에러 수집
        console_errors = []
        def handle_console(msg):
            if msg.type == 'error':
                console_errors.append(msg.text)
                print(f"❌ JS Error: {msg.text}")
        
        page.on('console', handle_console)
        
        try:
            print("🌐 페이지 로딩 중...")
            await page.goto("https://center-ten.vercel.app", timeout=30000)
            await page.wait_for_timeout(5000)
            
            title = await page.title()
            print(f"📄 페이지 제목: {title}")
            
            # 로그인 페이지인지 확인
            login_form = await page.query_selector('form, [data-testid="login-form"], input[type="email"]')
            if login_form:
                print("🔑 로그인 페이지가 표시됨")
            else:
                print("🏠 메인 애플리케이션 로드됨")
            
            print(f"🔍 총 JavaScript 에러: {len(console_errors)}개")
            
            if len(console_errors) == 0:
                print("✅ JavaScript 에러 없음!")
            else:
                print("❌ JavaScript 에러 발견:")
                for error in console_errors[:5]:  # 처음 5개만 표시
                    print(f"   • {error}")
                    
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(quick_check())