#!/usr/bin/env python3
"""
Playwright 기반 콘솔 메시지 체크 스크립트
"""
import asyncio
import sys
from datetime import datetime
from playwright.async_api import async_playwright

async def check_console_messages(url="http://localhost:5173"):
    """웹사이트의 콘솔 메시지를 체크합니다"""

    console_messages = []
    network_errors = []
    js_errors = []

    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(headless=False)  # 화면에 보이도록
        context = await browser.new_context()
        page = await context.new_page()

        # 콘솔 메시지 캐치
        def handle_console(msg):
            timestamp = datetime.now().strftime("%H:%M:%S")
            console_messages.append({
                'timestamp': timestamp,
                'type': msg.type,
                'text': msg.text,
                'location': msg.location
            })

        # 네트워크 에러 캐치
        def handle_response(response):
            if response.status >= 400:
                network_errors.append({
                    'url': response.url,
                    'status': response.status,
                    'status_text': response.status_text
                })

        # JS 에러 캐치
        def handle_page_error(error):
            js_errors.append(str(error))

        page.on('console', handle_console)
        page.on('response', handle_response)
        page.on('pageerror', handle_page_error)

        try:
            print(f"🌐 페이지 로딩 중: {url}")
            # 페이지 로드 (타임아웃 30초)
            await page.goto(url, wait_until='networkidle', timeout=30000)

            # 페이지가 완전히 로드될 때까지 대기
            await page.wait_for_timeout(3000)

            # 로그인 시도 (로그인 페이지인 경우)
            login_form = await page.query_selector('form')
            if login_form:
                print("🔐 로그인 페이지 감지, 로그인 시도...")

                # 이메일 입력
                email_input = await page.query_selector('input[type="email"]')
                if email_input:
                    await email_input.fill('admin@aibio.kr')

                # 비밀번호 입력
                password_input = await page.query_selector('input[type="password"]')
                if password_input:
                    await password_input.fill('admin123')

                # 로그인 버튼 클릭
                login_button = await page.query_selector('button[type="submit"]')
                if login_button:
                    await login_button.click()
                    # 로그인 후 페이지 로드 대기
                    await page.wait_for_timeout(5000)

            # 추가 대기 시간 (AJAX 요청 등)
            await page.wait_for_timeout(2000)

            print("✅ 페이지 로드 완료, 결과 분석 중...")

        except Exception as e:
            print(f"❌ 페이지 로드 에러: {e}")

        finally:
            await browser.close()

    # 결과 분석 및 출력
    print("\n" + "="*80)
    print("📊 콘솔 메시지 체크 결과")
    print("="*80)

    # JavaScript 에러
    if js_errors:
        print(f"\n❌ JavaScript 에러 ({len(js_errors)}개):")
        for i, error in enumerate(js_errors, 1):
            print(f"  {i}. {error}")
    else:
        print("\n✅ JavaScript 에러: 없음")

    # 네트워크 에러
    if network_errors:
        print(f"\n❌ 네트워크 에러 ({len(network_errors)}개):")
        for i, error in enumerate(network_errors, 1):
            print(f"  {i}. {error['status']} {error['status_text']} - {error['url']}")
    else:
        print("\n✅ 네트워크 에러: 없음")

    # 콘솔 메시지 분석
    error_messages = [msg for msg in console_messages if msg['type'] == 'error']
    warning_messages = [msg for msg in console_messages if msg['type'] == 'warning']
    log_messages = [msg for msg in console_messages if msg['type'] == 'log']

    print(f"\n📝 콘솔 메시지 요약:")
    print(f"  • 에러: {len(error_messages)}개")
    print(f"  • 경고: {len(warning_messages)}개")
    print(f"  • 로그: {len(log_messages)}개")

    # 에러 메시지 상세
    if error_messages:
        print(f"\n❌ 콘솔 에러 메시지 ({len(error_messages)}개):")
        for i, msg in enumerate(error_messages, 1):
            print(f"  {i}. [{msg['timestamp']}] {msg['text']}")
            if msg['location']:
                print(f"     위치: {msg['location']}")

    # 경고 메시지 상세
    if warning_messages:
        print(f"\n⚠️ 콘솔 경고 메시지 ({len(warning_messages)}개):")
        for i, msg in enumerate(warning_messages, 1):
            print(f"  {i}. [{msg['timestamp']}] {msg['text']}")

    # 전체 상태 판정
    total_issues = len(js_errors) + len(network_errors) + len(error_messages)

    print(f"\n{'='*80}")
    if total_issues == 0:
        print("🎉 완벽! 모든 검사 통과 - 배포 준비 완료")
        return_code = 0
    elif total_issues <= 3:
        print(f"⚠️ 경미한 문제 감지 ({total_issues}개) - 검토 후 배포 가능")
        return_code = 1
    else:
        print(f"🚨 심각한 문제 감지 ({total_issues}개) - 수정 후 배포 권장")
        return_code = 2

    print("="*80)
    return return_code

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"
    exit_code = asyncio.run(check_console_messages(url))
    sys.exit(exit_code)
