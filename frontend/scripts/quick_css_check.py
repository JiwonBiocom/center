#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def quick_check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("http://localhost:5173")
        await page.wait_for_timeout(2000)

        # 스크린샷
        await page.screenshot(path="/tmp/css_check_after_fix.png")

        # CSS 적용 확인
        result = await page.evaluate("""
            () => {
                const button = document.querySelector('button');
                const computed = button ? window.getComputedStyle(button) : null;

                return {
                    buttonBg: computed ? computed.backgroundColor : 'N/A',
                    buttonColor: computed ? computed.color : 'N/A',
                    bodyBg: window.getComputedStyle(document.body).backgroundColor,
                    hasTailwind: document.querySelector('style')?.textContent.includes('tailwind')
                };
            }
        """)

        print("=== CSS 적용 상태 ===")
        print(f"버튼 배경색: {result['buttonBg']}")
        print(f"버튼 글자색: {result['buttonColor']}")
        print(f"Body 배경색: {result['bodyBg']}")
        print(f"Tailwind 포함: {result['hasTailwind']}")
        print(f"\n스크린샷: /tmp/css_check_after_fix.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(quick_check())
