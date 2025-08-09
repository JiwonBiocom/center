#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def button_style_check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 브라우저 창 표시
        page = await browser.new_page()

        await page.goto("http://localhost:5173")
        await page.wait_for_timeout(3000)

        # 버튼의 실제 클래스와 스타일 확인
        button_info = await page.evaluate("""
            () => {
                const button = document.querySelector('button');
                if (!button) return null;

                const computed = window.getComputedStyle(button);
                const classList = Array.from(button.classList);

                // Tailwind 클래스 중 실제 적용된 것 확인
                const bgClass = classList.find(c => c.startsWith('bg-'));
                const textClass = classList.find(c => c.startsWith('text-'));

                return {
                    classes: button.className,
                    classList: classList,
                    bgClass,
                    textClass,
                    computedStyle: {
                        backgroundColor: computed.backgroundColor,
                        color: computed.color,
                        padding: computed.padding,
                        borderRadius: computed.borderRadius,
                        fontSize: computed.fontSize,
                        fontWeight: computed.fontWeight
                    },
                    text: button.textContent
                };
            }
        """)

        if button_info:
            print("=== 버튼 분석 ===")
            print(f"텍스트: {button_info['text']}")
            print(f"\n클래스 (전체): {button_info['classes']}")
            print(f"\n클래스 목록:")
            for cls in button_info['classList']:
                print(f"  - {cls}")

            print(f"\n검출된 Tailwind 클래스:")
            print(f"  배경: {button_info['bgClass']}")
            print(f"  텍스트: {button_info['textClass']}")

            print(f"\n계산된 스타일:")
            for key, value in button_info['computedStyle'].items():
                print(f"  {key}: {value}")
        else:
            print("버튼을 찾을 수 없습니다.")

        # 스크린샷
        await page.screenshot(path="/tmp/button_style_detail.png")
        print(f"\n스크린샷: /tmp/button_style_detail.png")

        print("\n브라우저 창에서 개발자 도구(F12)를 열어 Elements 탭에서 버튼을 확인하세요.")
        print("Enter를 눌러 종료...")
        input()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(button_style_check())
