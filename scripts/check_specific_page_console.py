#!/usr/bin/env python3
"""
특정 페이지의 콘솔 메시지를 정확하게 체크하는 스크립트
로그인 후 특정 경로로 이동하여 콘솔 메시지 확인
"""

import asyncio
from playwright.async_api import async_playwright
import sys

async def check_page_console(page_path="/customers"):
    """특정 페이지의 콘솔 메시지 체크"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 콘솔 메시지 수집
        all_messages = []
        errors = []
        warnings = []
        
        # 모든 콘솔 메시지 수집
        page.on("console", lambda msg: (
            all_messages.append({"type": msg.type, "text": msg.text}),
            errors.append(msg.text) if msg.type == "error" else None,
            warnings.append(msg.text) if msg.type == "warning" else None
        ))
        
        page.on("pageerror", lambda err: errors.append(f"JS Error: {err}"))
        
        print(f"🔍 특정 페이지 콘솔 체크: {page_path}")
        print("="*60)
        
        try:
            # 1. 로그인
            print("\n1️⃣ 로그인 중...")
            await page.goto("https://center-ten.vercel.app/login")
            await page.fill('input[type="email"]', "admin@aibio.com")
            await page.fill('input[type="password"]', "admin123")
            await page.click('button[type="submit"]')
            await page.wait_for_url("**/", timeout=10000)
            print("   ✅ 로그인 성공")
            
            # 콘솔 메시지 초기화 (로그인 페이지의 메시지 제외)
            all_messages.clear()
            errors.clear()
            warnings.clear()
            
            # 2. 특정 페이지로 이동
            print(f"\n2️⃣ {page_path} 페이지로 이동 중...")
            await page.goto(f"https://center-ten.vercel.app{page_path}")
            await page.wait_for_load_state("networkidle", timeout=10000)
            print(f"   ✅ {page_path} 페이지 로드 완료")
            
            # 3. 결과 분석
            print(f"\n📊 콘솔 분석 결과:")
            print(f"   전체 메시지: {len(all_messages)}개")
            print(f"   에러: {len(errors)}개")
            print(f"   경고: {len(warnings)}개")
            
            # 4. 상세 내용 출력
            if errors:
                print("\n❌ 에러 메시지:")
                for i, err in enumerate(errors, 1):
                    print(f"   {i}. {err}")
            
            if warnings:
                print("\n⚠️ 경고 메시지:")
                for i, warn in enumerate(warnings, 1):
                    print(f"   {i}. {warn}")
            
            # 5. API 에러 특별 체크
            api_errors = [msg for msg in all_messages if "404" in msg["text"] or "API" in msg["text"]]
            if api_errors:
                print("\n🔴 API 관련 에러:")
                for msg in api_errors:
                    print(f"   - [{msg['type']}] {msg['text']}")
            
            # 6. 최종 판정
            if not errors and not warnings:
                print(f"\n✅ {page_path} 페이지의 콘솔이 깨끗합니다!")
            else:
                print(f"\n⚠️ {page_path} 페이지에 문제가 있습니다.")
            
        except Exception as e:
            print(f"\n❌ 테스트 실패: {e}")
        
        await browser.close()

if __name__ == "__main__":
    # 페이지 경로 받기
    if len(sys.argv) > 1:
        page_path = sys.argv[1]
    else:
        page_path = "/customers"
    
    asyncio.run(check_page_console(page_path))