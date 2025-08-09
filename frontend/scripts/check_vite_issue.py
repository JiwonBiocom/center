#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def check_vite_issue():
    print("=== Vite CSS 문제 진단 ===\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 네트워크 요청 추적
        css_requests = []
        def track_css(response):
            if 'css' in response.url or response.url.endswith('.css'):
                css_requests.append({
                    "url": response.url,
                    "status": response.status,
                    "headers": response.headers
                })

        page.on("response", track_css)

        try:
            # 페이지 로드
            await page.goto("http://localhost:5173", wait_until="networkidle")

            # 모든 스타일 태그와 링크 확인
            styles_info = await page.evaluate("""
                () => {
                    // 모든 <style> 태그
                    const styles = Array.from(document.querySelectorAll('style'));

                    // 모든 <link> 태그
                    const links = Array.from(document.querySelectorAll('link'));

                    // Vite가 주입한 모듈 확인
                    const viteModules = Array.from(document.querySelectorAll('script[type="module"]'));

                    return {
                        styleCount: styles.length,
                        styles: styles.map(s => ({
                            id: s.id,
                            dataViteDevId: s.getAttribute('data-vite-dev-id'),
                            contentLength: s.textContent.length,
                            hasContent: s.textContent.includes('tailwind') || s.textContent.includes('@')
                        })),
                        links: links.map(l => ({
                            href: l.href,
                            rel: l.rel,
                            type: l.type
                        })),
                        viteModules: viteModules.map(s => s.src)
                    };
                }
            """)

            print("=== 페이지 내 스타일 정보 ===")
            print(f"<style> 태그 개수: {styles_info['styleCount']}")
            for i, style in enumerate(styles_info['styles']):
                print(f"\n스타일 {i+1}:")
                print(f"  - ID: {style['id']}")
                print(f"  - Vite Dev ID: {style['dataViteDevId']}")
                print(f"  - 크기: {style['contentLength']}자")
                print(f"  - Tailwind 포함: {style['hasContent']}")

            print(f"\n<link> 태그: {len(styles_info['links'])}개")
            for link in styles_info['links']:
                if link['rel'] == 'stylesheet':
                    print(f"  - {link['href']}")

            # CSS 네트워크 요청 확인
            print("\n=== CSS 관련 네트워크 요청 ===")
            for req in css_requests:
                print(f"URL: {req['url']}")
                print(f"상태: {req['status']}")
                print(f"Content-Type: {req['headers'].get('content-type', 'N/A')}")
                print()

            # 실제 Tailwind 적용 확인
            tailwind_check = await page.evaluate("""
                () => {
                    const button = document.querySelector('button');
                    const computed = button ? window.getComputedStyle(button) : null;

                    // Tailwind CSS가 로드되었는지 확인
                    const hasTailwindReset = window.getComputedStyle(document.body).boxSizing === 'border-box';

                    return {
                        hasTailwindReset,
                        button: computed ? {
                            backgroundColor: computed.backgroundColor,
                            color: computed.color,
                            borderRadius: computed.borderRadius,
                            padding: computed.padding
                        } : null
                    };
                }
            """)

            print("\n=== Tailwind CSS 적용 확인 ===")
            print(f"Tailwind Reset 적용: {tailwind_check['hasTailwindReset']}")
            if tailwind_check['button']:
                print(f"\n버튼 스타일:")
                for key, value in tailwind_check['button'].items():
                    print(f"  - {key}: {value}")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_vite_issue())
