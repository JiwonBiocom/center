#!/usr/bin/env python3
"""
시각적 레이아웃을 확인하고 스크린샷을 저장하는 스크립트
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def check_visual_layout(base_url="http://localhost:5173"):
    """브라우저를 열어서 시각적 레이아웃을 확인합니다."""

    async with async_playwright() as p:
        # 헤드리스 모드 비활성화하여 실제 브라우저처럼 렌더링
        browser = await p.chromium.launch(
            headless=False,  # 실제 브라우저 창 열기
            args=['--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2,  # Retina 디스플레이 대응
        )

        page = await context.new_page()

        print("🔍 시각적 레이아웃 확인 시작")
        print(f"🌐 URL: {base_url}")
        print("="*60)

        # 1. 로그인 페이지 접속
        print("\n1️⃣ 로그인 페이지 접속 중...")
        await page.goto(base_url, wait_until='networkidle')
        await page.wait_for_timeout(3000)

        # 스크린샷 저장
        screenshot_dir = "/Users/vibetj/coding/center/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)

        # 로그인 페이지 스크린샷
        login_screenshot = f"{screenshot_dir}/login_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await page.screenshot(path=login_screenshot, full_page=True)
        print(f"   📸 로그인 페이지 스크린샷 저장: {login_screenshot}")

        # CSS 로드 상태 확인
        print("\n2️⃣ CSS 로드 상태 확인...")

        # Tailwind CSS 클래스가 적용되었는지 확인
        try:
            # 배경색이 적용된 요소 찾기
            bg_element = await page.query_selector('[class*="bg-"]')
            if bg_element:
                bg_class = await bg_element.get_attribute('class')
                print(f"   ✅ Tailwind CSS 클래스 발견: {bg_class[:50]}...")
            else:
                print("   ❌ Tailwind CSS 클래스를 찾을 수 없음")

            # computed styles 확인
            body_style = await page.evaluate('''() => {
                const body = document.body;
                const computedStyle = window.getComputedStyle(body);
                return {
                    fontFamily: computedStyle.fontFamily,
                    backgroundColor: computedStyle.backgroundColor,
                    color: computedStyle.color
                };
            }''')
            print(f"   📊 Body 스타일: {body_style}")

        except Exception as e:
            print(f"   ❌ CSS 확인 중 에러: {e}")

        # 3. 로그인 시도
        print("\n3️⃣ 로그인 시도...")
        try:
            # 이메일 입력
            await page.fill('input[type="email"]', "admin@aibio.kr")
            # 비밀번호 입력
            await page.fill('input[type="password"]', "admin123")
            # 로그인 버튼 클릭
            await page.click('button[type="submit"]')

            # 로그인 후 대기
            await page.wait_for_timeout(3000)

            # 대시보드 스크린샷
            dashboard_screenshot = f"{screenshot_dir}/dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=dashboard_screenshot, full_page=True)
            print(f"   📸 대시보드 스크린샷 저장: {dashboard_screenshot}")

        except Exception as e:
            print(f"   ❌ 로그인 중 에러: {e}")

        # 4. 네트워크 요청 확인
        print("\n4️⃣ CSS 파일 로드 확인...")

        # index.css 직접 확인
        css_response = await page.goto(f"{base_url}/src/index.css")
        print(f"   index.css 상태: {css_response.status}")
        if css_response.status != 200:
            css_content = await css_response.text()
            print(f"   CSS 내용: {css_content[:200]}...")

        print("\n" + "="*60)
        print("✅ 시각적 확인 완료")
        print(f"📁 스크린샷이 {screenshot_dir} 폴더에 저장되었습니다.")

        # 브라우저는 수동으로 닫기
        input("\n🔍 브라우저를 확인하신 후 Enter를 눌러주세요...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_visual_layout())
