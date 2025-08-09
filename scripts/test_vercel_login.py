#!/usr/bin/env python3
"""
Vercel 사이트에서 실제 로그인 테스트
"""

import asyncio
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 브라우저 보이게
        page = await browser.new_page()
        
        # 개발자 도구 열기
        await page.goto("https://center-ten.vercel.app", wait_until="networkidle")
        
        print("🔍 브라우저가 열렸습니다.")
        print("개발자 도구(F12)를 열고 Console 탭을 확인하세요.")
        print("다음을 확인하세요:")
        print("1. 🔧 API URL: 어떤 URL이 설정되었는지")
        print("2. 네트워크 탭에서 API 호출이 있는지")
        print("3. 에러 메시지가 있는지")
        
        # 30초 대기
        await page.wait_for_timeout(30000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())