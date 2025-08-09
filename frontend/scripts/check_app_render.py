#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def check_app_render():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 브라우저 창 표시
        page = await browser.new_page()

        # 네트워크 요청 추적
        js_errors = []
        def track_js_error(response):
            if response.status >= 400 and response.url.endswith('.js'):
                js_errors.append(f"{response.url} - {response.status}")

        page.on("response", track_js_error)

        print("페이지 로드 중...")
        await page.goto("http://localhost:5173")
        await page.wait_for_timeout(3000)

        # 페이지 상태 확인
        page_state = await page.evaluate("""
            () => {
                // HTML 구조
                const root = document.getElementById('root');
                const html = document.documentElement.innerHTML;

                // CSS 로드 상태
                const styles = Array.from(document.querySelectorAll('style'));
                const cssLoaded = styles.some(s => s.textContent.includes('tailwind'));

                // React 앱 상태
                let reactError = null;
                try {
                    // React 에러 바운더리 확인
                    const errorDiv = document.querySelector('.error-boundary');
                    if (errorDiv) {
                        reactError = errorDiv.textContent;
                    }
                } catch (e) {
                    reactError = e.message;
                }

                return {
                    rootExists: !!root,
                    rootContent: root ? root.innerHTML : null,
                    htmlLength: html.length,
                    cssLoaded,
                    reactError,
                    title: document.title
                };
            }
        """)

        print("\n=== 페이지 상태 ===")
        print(f"제목: {page_state['title']}")
        print(f"Root 요소: {page_state['rootExists']}")
        print(f"CSS 로드: {page_state['cssLoaded']}")
        print(f"HTML 크기: {page_state['htmlLength']}자")

        if page_state['rootContent']:
            print(f"\nRoot 내용:")
            print(page_state['rootContent'][:200])

        if page_state['reactError']:
            print(f"\nReact 에러: {page_state['reactError']}")

        if js_errors:
            print(f"\nJS 로드 에러:")
            for error in js_errors:
                print(f"  - {error}")

        # 스크린샷
        await page.screenshot(path="/tmp/app_render_check.png", full_page=True)
        print(f"\n스크린샷: /tmp/app_render_check.png")

        print("\n브라우저 창을 확인하고 Enter를 누르세요...")
        input()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_app_render())
