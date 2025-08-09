#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def final_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("http://localhost:5173")
        await page.wait_for_timeout(5000)  # 충분한 대기

        # 스크린샷
        await page.screenshot(path="/tmp/final_result.png", full_page=True)

        # 버튼 스타일 확인
        button_check = await page.evaluate("""
            () => {
                const button = document.querySelector('button');
                if (!button) {
                    // 버튼이 없으면 페이지 내용 확인
                    return {
                        hasButton: false,
                        pageContent: document.body.textContent.substring(0, 200),
                        elementCount: document.querySelectorAll('*').length
                    };
                }

                const computed = window.getComputedStyle(button);
                return {
                    hasButton: true,
                    backgroundColor: computed.backgroundColor,
                    color: computed.color,
                    text: button.textContent
                };
            }
        """)

        print("=== 최종 결과 ===")
        if button_check['hasButton']:
            print(f"✅ 버튼 발견: {button_check['text']}")
            print(f"   배경색: {button_check['backgroundColor']}")
            print(f"   글자색: {button_check['color']}")
        else:
            print(f"❌ 버튼 없음")
            print(f"   페이지 내용: {button_check['pageContent']}")
            print(f"   요소 개수: {button_check['elementCount']}")

        print(f"\n스크린샷 저장: /tmp/final_result.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(final_screenshot())
