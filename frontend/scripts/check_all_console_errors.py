#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import sys
import json
from datetime import datetime

async def check_console_with_detailed_monitoring(url="http://localhost:5173"):
    """모든 종류의 콘솔 메시지와 에러를 세밀하게 감지"""

    print(f"🔍 {url} 접속 중...")
    print(f"시작 시간: {datetime.now()}")
    print("-" * 80)

    all_messages = []
    page_errors = []
    request_failures = []

    async with async_playwright() as p:
        # Chromium 사용 (개발자 도구와 동일한 엔진)
        browser = await p.chromium.launch(
            headless=False,  # 실제 브라우저 창 표시
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = await browser.new_context(
            # 개발자 도구 열기
            devtools=True
        )

        page = await context.new_page()

        # 1. 콘솔 메시지 캡처 (가장 먼저 설정)
        page.on("console", lambda msg: all_messages.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location,
            "args": [str(arg) for arg in msg.args]
        }))

        # 2. 페이지 에러 캡처
        page.on("pageerror", lambda err: page_errors.append({
            "error": str(err),
            "stack": err.stack if hasattr(err, 'stack') else None
        }))

        # 3. 요청 실패 캡처
        page.on("requestfailed", lambda req: request_failures.append({
            "url": req.url,
            "failure": req.failure
        }))

        # 4. JavaScript 에러 인젝션 (페이지 로드 전)
        await page.add_init_script("""
            // 원본 console 메서드 저장
            const originalError = console.error;
            const originalWarn = console.warn;
            const originalLog = console.log;

            // 모든 에러 캡처
            window.__captured_errors__ = [];

            // console.error 오버라이드
            console.error = function(...args) {
                window.__captured_errors__.push({
                    type: 'error',
                    message: args.join(' '),
                    timestamp: new Date().toISOString(),
                    stack: new Error().stack
                });
                originalError.apply(console, args);
            };

            // window.onerror 핸들러
            window.onerror = function(message, source, lineno, colno, error) {
                window.__captured_errors__.push({
                    type: 'window.onerror',
                    message: message,
                    source: source,
                    line: lineno,
                    column: colno,
                    error: error ? error.toString() : null,
                    stack: error ? error.stack : null,
                    timestamp: new Date().toISOString()
                });
                return false;
            };

            // unhandledrejection 핸들러
            window.addEventListener('unhandledrejection', function(event) {
                window.__captured_errors__.push({
                    type: 'unhandledrejection',
                    reason: event.reason,
                    promise: event.promise,
                    timestamp: new Date().toISOString()
                });
            });

            // Vite 관련 특수 처리
            if (window.__vite_plugin_react_preamble_installed__) {
                console.log('[Error Monitor] Vite React plugin detected');
            }
        """)

        try:
            # 5. 네트워크 요청 모니터링
            await page.route('**/*', lambda route: route.continue_())

            # 6. 페이지 접속 (타임아웃 늘림)
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            print(f"✅ 페이지 로드 완료 (상태: {response.status})")

            # 7. 추가 대기 (동적 에러 캡처)
            await page.wait_for_timeout(3000)

            # 8. 인젝션된 에러 수집
            captured_errors = await page.evaluate("window.__captured_errors__ || []")

            # 9. 현재 DOM 상태 확인
            react_root = await page.query_selector('#root')
            has_react_content = await page.evaluate("document.querySelector('#root')?.children.length > 0")

            # 결과 출력
            print("\n📊 전체 분석 결과:")
            print("=" * 80)

            # 콘솔 메시지 분석
            errors = [m for m in all_messages if m['type'] == 'error']
            warnings = [m for m in all_messages if m['type'] == 'warning']

            print(f"\n🔴 콘솔 에러: {len(errors)}개")
            for i, err in enumerate(errors, 1):
                print(f"  {i}. {err['text']}")
                if err.get('location'):
                    print(f"     위치: {err['location']}")

            print(f"\n🟡 콘솔 경고: {len(warnings)}개")
            for i, warn in enumerate(warnings[:5], 1):  # 처음 5개만
                print(f"  {i}. {warn['text']}")

            print(f"\n💥 페이지 에러: {len(page_errors)}개")
            for i, err in enumerate(page_errors, 1):
                print(f"  {i}. {err['error']}")

            print(f"\n🌐 네트워크 실패: {len(request_failures)}개")
            for i, fail in enumerate(request_failures, 1):
                print(f"  {i}. {fail['url']} - {fail['failure']}")

            print(f"\n🔍 JavaScript로 캡처된 에러: {len(captured_errors)}개")
            for i, err in enumerate(captured_errors, 1):
                print(f"  {i}. [{err['type']}] {err['message']}")
                if err.get('source'):
                    print(f"     소스: {err['source']}:{err.get('line', '?')}")

            print(f"\n⚛️ React 상태:")
            print(f"  - React 루트 존재: {'✅' if react_root else '❌'}")
            print(f"  - React 콘텐츠 렌더링: {'✅' if has_react_content else '❌'}")

            # @vitejs/plugin-react 에러 특별 체크
            vite_react_errors = [
                err for err in captured_errors +
                [{"type": m['type'], "message": m['text']} for m in all_messages]
                if '@vitejs/plugin-react' in str(err.get('message', ''))
            ]

            if vite_react_errors:
                print(f"\n🔥 Vite React Plugin 에러 감지됨:")
                for err in vite_react_errors:
                    print(f"  - {err}")

            # 전체 로그 저장
            with open('console_full_report.json', 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "url": url,
                    "console_messages": all_messages,
                    "page_errors": page_errors,
                    "request_failures": request_failures,
                    "captured_errors": captured_errors,
                    "react_status": {
                        "root_exists": bool(react_root),
                        "has_content": has_react_content
                    }
                }, f, indent=2, ensure_ascii=False)

            print(f"\n📄 전체 로그가 console_full_report.json에 저장되었소")

            # 10초 대기 (수동 확인 가능)
            print(f"\n⏸️  10초 동안 브라우저 창을 확인하실 수 있소...")
            await page.wait_for_timeout(10000)

        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"
    asyncio.run(check_console_with_detailed_monitoring(url))
