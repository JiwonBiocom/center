#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def check_console_errors():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 모든 콘솔 메시지와 에러 수집
        all_logs = []
        page.on("console", lambda msg: all_logs.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }))

        page.on("pageerror", lambda error: all_logs.append({
            "type": "pageerror",
            "text": str(error),
            "location": None
        }))

        print("페이지 로드 중...")
        await page.goto("http://localhost:5173", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)  # 충분한 대기

        # React root 확인
        react_check = await page.evaluate("""
            () => {
                const root = document.getElementById('root');
                const hasReact = root && root.children.length > 0;
                const reactDevTools = window.__REACT_DEVTOOLS_GLOBAL_HOOK__;

                return {
                    hasRoot: !!root,
                    rootChildren: root ? root.children.length : 0,
                    rootHTML: root ? root.innerHTML.substring(0, 200) : null,
                    hasReactDevTools: !!reactDevTools,
                    documentReadyState: document.readyState
                };
            }
        """)

        print("\n=== React 앱 상태 ===")
        print(f"root 요소 존재: {react_check['hasRoot']}")
        print(f"root 자식 요소: {react_check['rootChildren']}개")
        print(f"React DevTools: {react_check['hasReactDevTools']}")
        print(f"Document 상태: {react_check['documentReadyState']}")

        if react_check['rootHTML']:
            print(f"\nroot 내용:")
            print(react_check['rootHTML'])

        print("\n=== 콘솔 로그 (전체) ===")
        for log in all_logs:
            if log['type'] in ['error', 'pageerror', 'warning']:
                print(f"❌ [{log['type']}] {log['text']}")
                if log['location']:
                    print(f"   위치: {log['location']}")
            else:
                print(f"[{log['type']}] {log['text']}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_console_errors())
