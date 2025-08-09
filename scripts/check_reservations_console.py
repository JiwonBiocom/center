#!/usr/bin/env python3
"""
예약관리 페이지 콘솔 메시지 확인
"""
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def check_console():
    """예약관리 페이지의 콘솔 메시지 확인"""
    
    print(f"🔍 예약관리 페이지 콘솔 메시지 확인")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 콘솔 메시지 수집
        console_messages = []
        
        def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text,
                'location': msg.location
            })
            
            # 실시간 출력
            emoji = {
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️',
                'log': '📝'
            }.get(msg.type, '❓')
            
            print(f"{emoji} [{msg.type.upper()}] {msg.text}")
            if msg.location.get('url'):
                print(f"   위치: {msg.location['url']}:{msg.location.get('lineNumber', '?')}")
        
        page.on('console', handle_console)
        
        # 로그인
        print("\n1. 로그인 중...")
        page.goto('http://localhost:5173/login')
        page.wait_for_selector('input[type="email"]', timeout=10000)
        page.fill('input[type="email"]', 'admin@aibio.kr')
        page.fill('input[type="password"]', 'admin123')
        page.click('button[type="submit"]')
        
        # 로그인 후 대기
        page.wait_for_timeout(2000)
        
        # 콘솔 메시지 초기화
        console_messages.clear()
        
        # 예약관리 페이지로 이동
        print("\n2. 예약관리 페이지로 이동...")
        page.goto('http://localhost:5173/reservations')
        
        # 예약 목록이 로드될 때까지 대기
        page.wait_for_timeout(3000)
        
        # 결과 분석
        print(f"\n📊 콘솔 메시지 분석:")
        error_count = sum(1 for msg in console_messages if msg['type'] == 'error')
        warning_count = sum(1 for msg in console_messages if msg['type'] == 'warning')
        
        print(f"  - 총 메시지: {len(console_messages)}개")
        print(f"  - 에러: {error_count}개")
        print(f"  - 경고: {warning_count}개")
        
        if error_count > 0:
            print(f"\n🚨 에러 상세:")
            for msg in console_messages:
                if msg['type'] == 'error':
                    print(f"  - {msg['text']}")
                    if msg['location'].get('url'):
                        print(f"    위치: {msg['location']['url']}:{msg['location'].get('lineNumber', '?')}")
        
        # 네트워크 에러 확인
        print(f"\n📡 네트워크 요청 확인 중...")
        failed_requests = []
        
        def handle_request_failed(request):
            failed_requests.append({
                'url': request.url,
                'method': request.method,
                'failure': request.failure
            })
            print(f"❌ 네트워크 에러: {request.url}")
            print(f"   원인: {request.failure}")
        
        page.on('requestfailed', handle_request_failed)
        
        # 추가 대기
        page.wait_for_timeout(2000)
        
        # 스크린샷
        page.screenshot(path='reservations_console_check.png', full_page=True)
        print(f"\n📸 스크린샷 저장: reservations_console_check.png")
        
        # 최종 평가
        print(f"\n✅ 최종 평가:")
        if error_count == 0 and len(failed_requests) == 0:
            print("  예약관리 페이지가 정상적으로 로드되었습니다.")
            print("  콘솔 에러나 네트워크 에러가 없습니다.")
        else:
            print("  ⚠️ 문제가 발견되었습니다. 수정이 필요합니다.")
        
        browser.close()

if __name__ == "__main__":
    check_console()