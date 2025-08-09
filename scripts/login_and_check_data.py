#!/usr/bin/env python3
"""
로그인 후 데이터 확인 스크립트
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def login_and_check_data():
    print("🔐 로그인 후 데이터 확인 시작")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # API 호출 모니터링
        api_calls = []
        network_errors = []
        
        def handle_request(request):
            if '/api/' in request.url:
                api_calls.append({
                    'method': request.method,
                    'url': request.url,
                    'headers': dict(request.headers)
                })
                print(f"🌐 API 요청: {request.method} {request.url}")
        
        def handle_response(response):
            if '/api/' in response.url:
                if response.status >= 400:
                    network_errors.append({
                        'url': response.url,
                        'status': response.status
                    })
                    print(f"❌ API 에러: {response.status} {response.url}")
                else:
                    print(f"✅ API 성공: {response.status} {response.url}")
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        try:
            # 1. 메인 페이지 접속
            print("📍 메인 페이지 접속...")
            await page.goto("https://center-ten.vercel.app")
            await page.wait_for_timeout(3000)
            
            # 2. 로그인 폼 확인
            print("🔍 로그인 폼 찾기...")
            email_input = await page.query_selector('input[type="email"], input[name="email"]')
            password_input = await page.query_selector('input[type="password"], input[name="password"]')
            
            if not email_input or not password_input:
                print("❌ 로그인 폼을 찾을 수 없습니다")
                
                # 페이지 구조 확인
                title = await page.title()
                print(f"현재 페이지 제목: {title}")
                
                # 모든 input 확인
                inputs = await page.query_selector_all('input')
                print(f"발견된 input 요소: {len(inputs)}개")
                for i, input_elem in enumerate(inputs):
                    input_type = await input_elem.get_attribute('type')
                    input_name = await input_elem.get_attribute('name')
                    input_placeholder = await input_elem.get_attribute('placeholder')
                    print(f"  Input {i+1}: type='{input_type}', name='{input_name}', placeholder='{input_placeholder}'")
                
                return
            
            # 3. 로그인 시도 (테스트 계정)
            print("🔑 로그인 시도...")
            await email_input.fill("admin@aibio.com")
            await password_input.fill("admin123")
            
            # 로그인 버튼 찾기
            login_button = await page.query_selector('button[type="submit"], .login-button, .btn-login')
            if not login_button:
                # 일반적인 버튼들 중에서 찾기
                buttons = await page.query_selector_all('button')
                for button in buttons:
                    text = await button.text_content()
                    if text and ('로그인' in text or 'Login' in text.lower()):
                        login_button = button
                        break
            
            if login_button:
                await login_button.click()
                print("🔘 로그인 버튼 클릭")
                await page.wait_for_timeout(5000)
            else:
                print("❌ 로그인 버튼을 찾을 수 없습니다")
                return
            
            # 4. 로그인 후 고객 페이지 접속
            print("👥 고객 관리 페이지 접속...")
            await page.goto("https://center-ten.vercel.app/customers")
            await page.wait_for_timeout(5000)
            
            # 5. 페이지 내용 확인
            title = await page.title()
            print(f"페이지 제목: {title}")
            
            # 테이블이나 데이터 확인
            tables = await page.query_selector_all('table, .table, [data-testid*="table"]')
            print(f"테이블 발견: {len(tables)}개")
            
            if tables:
                for i, table in enumerate(tables):
                    rows = await table.query_selector_all('tr, .table-row')
                    print(f"  테이블 {i+1}: {len(rows)}행")
            
            # 빈 상태 메시지 확인
            empty_messages = await page.query_selector_all('.empty, .no-data, .empty-state')
            if empty_messages:
                for i, msg in enumerate(empty_messages):
                    text = await msg.text_content()
                    print(f"📭 빈 상태 메시지 {i+1}: {text}")
            
            # 6. 다른 메뉴들도 확인
            menus_to_check = [
                ('/payments', '결제 관리'),
                ('/packages', '패키지 관리'),
                ('/services', '서비스 관리')
            ]
            
            for path, menu_name in menus_to_check:
                print(f"\n📋 {menu_name} 페이지 확인...")
                await page.goto(f"https://center-ten.vercel.app{path}")
                await page.wait_for_timeout(3000)
                
                # API 호출이 일어났는지 확인
                current_api_count = len(api_calls)
                await page.wait_for_timeout(2000)
                new_api_count = len(api_calls)
                
                if new_api_count > current_api_count:
                    print(f"   ✅ API 호출 발생: {new_api_count - current_api_count}개")
                else:
                    print(f"   ❌ API 호출 없음")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        await browser.close()
        
        # 결과 요약
        print(f"\n📊 최종 결과:")
        print(f"   총 API 호출: {len(api_calls)}개")
        print(f"   API 에러: {len(network_errors)}개")
        
        if api_calls:
            print(f"\n🌐 API 호출 목록:")
            for call in api_calls:
                print(f"   • {call['method']} {call['url']}")
        
        if network_errors:
            print(f"\n❌ API 에러 목록:")
            for error in network_errors:
                print(f"   • {error['status']} {error['url']}")

if __name__ == "__main__":
    asyncio.run(login_and_check_data())