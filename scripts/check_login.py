#!/usr/bin/env python3
"""로그인 페이지 및 프로세스 확인 스크립트"""
import asyncio
from playwright.async_api import async_playwright
import time

async def check_login():
    async with async_playwright() as p:
        # 브라우저 시작
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 콘솔 메시지 수집
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        
        # 네트워크 요청 모니터링
        network_requests = []
        page.on("request", lambda req: network_requests.append(f"{req.method} {req.url}"))
        
        try:
            print("1. 로그인 페이지 접속...")
            await page.goto("http://localhost:5173/login", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # 스크린샷
            await page.screenshot(path="login_page.png")
            print("   - 스크린샷 저장: login_page.png")
            
            # 로그인 폼 확인
            email_input = await page.query_selector('input[type="email"]')
            password_input = await page.query_selector('input[type="password"]')
            
            if email_input and password_input:
                print("2. 로그인 폼 발견, 로그인 시도...")
                
                # 로그인 정보 입력
                await email_input.fill("admin@aibio.kr")
                await password_input.fill("admin123")
                
                # 로그인 버튼 찾기
                login_button = await page.query_selector('button[type="submit"]')
                if login_button:
                    print("3. 로그인 버튼 클릭...")
                    await login_button.click()
                    
                    # 응답 대기
                    await page.wait_for_timeout(3000)
                    
                    # 현재 URL 확인
                    current_url = page.url
                    print(f"4. 로그인 후 URL: {current_url}")
                    
                    # 로그인 후 스크린샷
                    await page.screenshot(path="after_login.png")
                    print("   - 스크린샷 저장: after_login.png")
                else:
                    print("❌ 로그인 버튼을 찾을 수 없습니다.")
            else:
                print("❌ 로그인 폼을 찾을 수 없습니다.")
            
            # 콘솔 메시지 출력
            if console_messages:
                print("\n📋 콘솔 메시지:")
                for msg in console_messages[-10:]:  # 마지막 10개
                    print(f"   {msg}")
            
            # 네트워크 요청 출력
            print("\n🌐 네트워크 요청:")
            auth_requests = [req for req in network_requests if "auth" in req]
            for req in auth_requests[-10:]:  # 마지막 10개
                print(f"   {req}")
                
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            await page.screenshot(path="error_state.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_login())