#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import sys
from datetime import datetime

async def check_vite_specific_errors(url="http://localhost:5173"):
    """Vite React 플러그인 에러를 특별히 감지하는 스크립트"""

    print(f"🔍 Vite React 플러그인 에러 감지 모드")
    print(f"URL: {url}")
    print("-" * 80)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # 브라우저 창 표시
            args=['--auto-open-devtools-for-tabs']  # 개발자 도구 자동 열기
        )

        page = await browser.new_page()

        # 모든 콘솔 메시지 수집
        console_messages = []
        page_errors = []

        # 콘솔 메시지 핸들러
        def handle_console(msg):
            message = {
                "type": msg.type,
                "text": msg.text,
                "location": str(msg.location) if msg.location else None
            }
            console_messages.append(message)

            # 실시간 출력
            if msg.type in ['error', 'warning']:
                print(f"[{msg.type.upper()}] {msg.text}")
                if msg.location:
                    print(f"  위치: {msg.location}")

        page.on("console", handle_console)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # 페이지 로드 전 스크립트 주입
        await page.add_init_script("""
            // Vite React 플러그인 상태 모니터링
            window.__vite_errors__ = [];

            // Error 생성자 후킹
            const OriginalError = window.Error;
            window.Error = function(...args) {
                const error = new OriginalError(...args);
                if (args[0] && args[0].includes('@vitejs/plugin-react')) {
                    window.__vite_errors__.push({
                        message: args[0],
                        stack: error.stack,
                        timestamp: new Date().toISOString()
                    });
                    console.error('[VITE ERROR CAPTURED]', args[0]);
                }
                return error;
            };

            // console.error 모니터링
            const originalConsoleError = console.error;
            console.error = function(...args) {
                const message = args.join(' ');
                if (message.includes('@vitejs/plugin-react') ||
                    message.includes('preamble') ||
                    message.includes('App.tsx:44')) {
                    window.__vite_errors__.push({
                        type: 'console.error',
                        message: message,
                        timestamp: new Date().toISOString()
                    });
                }
                originalConsoleError.apply(console, args);
            };
        """)

        try:
            # 페이지 로드
            print("페이지 로딩 중...")
            response = await page.goto(url, wait_until="domcontentloaded")
            print(f"초기 로드 완료 (상태: {response.status})")

            # 추가 대기
            await page.wait_for_timeout(2000)

            # React 렌더링 대기
            await page.wait_for_selector('#root', state='attached', timeout=5000)
            print("React 루트 감지됨")

            # 캡처된 Vite 에러 확인
            vite_errors = await page.evaluate("window.__vite_errors__ || []")

            print("\n📊 분석 결과:")
            print("=" * 80)

            # Vite 관련 에러 필터링
            vite_related = [
                msg for msg in console_messages
                if any(keyword in msg['text'] for keyword in [
                    '@vitejs/plugin-react', 'preamble', 'App.tsx:44',
                    'vite', 'HMR', 'React refresh'
                ])
            ]

            if vite_related:
                print(f"\n🔥 Vite/React 관련 메시지 발견: {len(vite_related)}개")
                for msg in vite_related:
                    print(f"\n[{msg['type']}] {msg['text']}")
                    if msg['location']:
                        print(f"위치: {msg['location']}")

            if vite_errors:
                print(f"\n💥 직접 캡처된 Vite 에러: {len(vite_errors)}개")
                for err in vite_errors:
                    print(f"\n{err['message']}")
                    print(f"시간: {err['timestamp']}")

            # App.tsx:44 근처 코드 확인
            app_content = await page.evaluate("""
                // App.tsx:44 라인 근처 확인
                const scripts = Array.from(document.scripts);
                const appScript = scripts.find(s => s.src && s.src.includes('App.tsx'));
                return {
                    hasAppScript: !!appScript,
                    scriptCount: scripts.length,
                    vitePluginDetected: !!window.__vite_plugin_react_preamble_installed__
                };
            """)

            print(f"\n📄 App.tsx 상태:")
            print(f"  - App 스크립트 로드됨: {app_content['hasAppScript']}")
            print(f"  - 전체 스크립트 수: {app_content['scriptCount']}")
            print(f"  - Vite React 플러그인 감지: {app_content['vitePluginDetected']}")

            # 10초 대기 (수동 확인)
            print("\n⏸️  브라우저에서 개발자 도구를 확인하세요...")
            print("특히 Console 탭에서 빨간색 에러를 찾아보세요.")
            await page.wait_for_timeout(10000)

        except Exception as e:
            print(f"❌ 에러 발생: {e}")
        finally:
            await browser.close()

        # 요약
        total_errors = len([m for m in console_messages if m['type'] == 'error'])
        print(f"\n📊 최종 요약:")
        print(f"  - 전체 에러 수: {total_errors}")
        print(f"  - Vite 관련 메시지: {len(vite_related)}")
        print(f"  - 페이지 에러: {len(page_errors)}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"
    asyncio.run(check_vite_specific_errors(url))
