#!/usr/bin/env python3
"""
로그인 플로우를 테스트하고 콘솔 메시지를 확인하는 스크립트
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import json

async def check_login_flow(base_url="http://localhost:5173"):
    """로그인 플로우와 콘솔 메시지를 확인합니다."""

    console_messages = []
    errors = []
    warnings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 콘솔 메시지 캡처
        def handle_console(msg):
            message_data = {
                'type': msg.type,
                'text': msg.text,
                'timestamp': datetime.now().isoformat()
            }
            console_messages.append(message_data)

            if msg.type == 'error':
                errors.append(message_data)
                print(f"   ❌ Error: {msg.text[:100]}...")
            elif msg.type == 'warning':
                warnings.append(message_data)
                print(f"   ⚠️  Warning: {msg.text[:100]}...")

        page.on('console', handle_console)
        page.on('pageerror', lambda error: errors.append({
            'type': 'pageerror',
            'text': str(error),
            'timestamp': datetime.now().isoformat()
        }))

        print("🔍 로그인 플로우 테스트 시작")
        print(f"🌐 URL: {base_url}")
        print("="*60)

        # 1. 메인 페이지 접속
        print("\n1️⃣ 메인 페이지 접속 중...")
        await page.goto(base_url, wait_until='networkidle')
        await page.wait_for_timeout(2000)

        # 로그인 페이지로 리다이렉트 되는지 확인
        current_url = page.url
        print(f"   현재 URL: {current_url}")

        # 2. 로그인 시도
        if "/login" in current_url or page.url == base_url + "/":
            print("\n2️⃣ 로그인 시도 중...")

            # 로그인 폼 찾기
            try:
                # 이메일 입력
                email_input = await page.wait_for_selector('input[type="email"], input[name="email"], input[placeholder*="이메일"]', timeout=5000)
                await email_input.fill("admin@aibio.kr")
                print("   ✅ 이메일 입력 완료")

                # 비밀번호 입력
                password_input = await page.wait_for_selector('input[type="password"], input[name="password"], input[placeholder*="비밀번호"]', timeout=5000)
                await password_input.fill("admin123")
                print("   ✅ 비밀번호 입력 완료")

                # 로그인 버튼 클릭
                login_button = await page.wait_for_selector('button[type="submit"], button:has-text("로그인")', timeout=5000)
                await login_button.click()
                print("   ✅ 로그인 버튼 클릭")

                # 로그인 후 대기
                await page.wait_for_timeout(3000)

                # 로그인 성공 확인
                current_url = page.url
                print(f"\n3️⃣ 로그인 후 URL: {current_url}")

                if "/dashboard" in current_url or current_url == base_url + "/":
                    print("   ✅ 로그인 성공! 대시보드로 이동")

                    # 대시보드 로드 대기
                    await page.wait_for_timeout(3000)

                    # 주요 요소 확인
                    try:
                        await page.wait_for_selector('main, [role="main"], .dashboard', timeout=5000)
                        print("   ✅ 대시보드 메인 콘텐츠 로드 완료")
                    except:
                        print("   ⚠️  대시보드 메인 콘텐츠를 찾을 수 없음")
                else:
                    print("   ❌ 로그인 실패 또는 예상치 못한 페이지")

            except Exception as e:
                print(f"   ❌ 로그인 폼을 찾을 수 없음: {e}")

        # 결과 요약
        print("\n" + "="*60)
        print("📊 콘솔 메시지 요약")
        print("="*60)
        print(f"❌ 에러: {len(errors)}개")
        if errors:
            for i, error in enumerate(errors[:5], 1):  # 처음 5개만 표시
                print(f"  {i}. {error['text'][:150]}...")

        print(f"\n⚠️  경고: {len(warnings)}개")
        if warnings:
            for i, warning in enumerate(warnings[:5], 1):  # 처음 5개만 표시
                print(f"  {i}. {warning['text'][:150]}...")

        print(f"\n📝 전체 콘솔 메시지: {len(console_messages)}개")

        # 전체 평가
        if len(errors) == 0:
            print("\n✅ 에러 없이 로그인 플로우가 완료되었습니다!")
        else:
            print(f"\n❌ {len(errors)}개의 에러가 발견되었습니다. 수정이 필요합니다.")

        await browser.close()

        return {
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_messages': len(console_messages)
        }

if __name__ == "__main__":
    result = asyncio.run(check_login_flow())
