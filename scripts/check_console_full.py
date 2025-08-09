#!/usr/bin/env python3
"""
Playwright로 브라우저 캐시를 비우고 완전히 새로운 상태에서 콘솔 확인
"""
import asyncio
import sys
from playwright.async_api import async_playwright
from datetime import datetime

async def check_console_fresh_browser(url: str = "http://localhost:5173"):
    """완전히 새로운 브라우저 상태에서 콘솔 메시지 확인"""
    
    console_messages = []
    errors = []
    warnings = []
    
    async with async_playwright() as p:
        # 새로운 브라우저 컨텍스트 (캐시 없음)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            # 캐시와 localStorage를 비운 상태로 시작
            storage_state=None
        )
        page = await context.new_page()
        
        # 콘솔 메시지 리스너
        def handle_console(msg):
            message_data = {
                'type': msg.type,
                'text': msg.text,
                'url': msg.location.get('url', ''),
                'line': msg.location.get('lineNumber', 0),
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3]
            }
            
            console_messages.append(message_data)
            print(f"[{message_data['timestamp']}] [{msg.type.upper()}] {msg.text}")
            
            if msg.type == 'error':
                errors.append(message_data)
            elif msg.type == 'warning':
                warnings.append(message_data)
        
        page.on("console", handle_console)
        
        # 페이지 에러 리스너
        def handle_page_error(err):
            error_data = {
                'type': 'pageerror',
                'text': str(err),
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3]
            }
            errors.append(error_data)
            print(f"[{error_data['timestamp']}] [PAGEERROR] {str(err)}")
        
        page.on("pageerror", handle_page_error)
        
        # 네트워크 실패 리스너
        failed_requests = []
        def handle_request_failed(request):
            failure_info = {
                'url': request.url,
                'method': request.method,
                'failure': request.failure,
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3]
            }
            failed_requests.append(failure_info)
            print(f"[{failure_info['timestamp']}] [REQUEST_FAILED] {request.method} {request.url} - {request.failure}")
        
        page.on("requestfailed", handle_request_failed)
        
        print(f"\n🔍 완전히 새로운 브라우저 상태에서 {url} 콘솔 확인\n")
        
        try:
            # 캐시 비우기
            await context.clear_cookies()
            await context.clear_permissions()
            
            # 페이지 로드
            response = await page.goto(url, wait_until='networkidle', timeout=30000)
            
            if response and response.ok:
                print(f"✅ 페이지 로드 성공 (상태 코드: {response.status})")
            else:
                print(f"❌ 페이지 로드 실패")
            
            # Service Worker와 WebSocket 연결을 위한 충분한 대기
            print("⏳ Service Worker 등록 및 WebSocket 연결 대기 중...")
            await page.wait_for_timeout(8000)
            
            # 페이지 새로고침으로 추가 테스트
            print("🔄 페이지 새로고침으로 추가 테스트...")
            await page.reload(wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            print(f"\n{'='*60}")
            print("📊 최종 콘솔 메시지 분석 결과")
            print(f"{'='*60}\n")
            
            print(f"총 메시지 수: {len(console_messages)}")
            print(f"❌ 에러: {len(errors)}개")
            print(f"⚠️  경고: {len(warnings)}개")
            print(f"🔗 실패한 요청: {len(failed_requests)}개")
            print(f"ℹ️  정보/로그: {len([m for m in console_messages if m['type'] in ['log', 'info']])}개")
            print(f"🐛 디버그: {len([m for m in console_messages if m['type'] == 'debug'])}개\n")
            
            # 에러 상세 출력
            if errors:
                print(f"🚨 에러 메시지 상세:")
                print(f"{'-'*60}")
                for i, error in enumerate(errors, 1):
                    print(f"\n[에러 {i}] {error['timestamp']}")
                    print(f"타입: {error['type']}")
                    print(f"내용: {error['text']}")
            
            # 실패한 요청 출력
            if failed_requests:
                print(f"\n🔗 실패한 네트워크 요청:")
                print(f"{'-'*60}")
                for i, req in enumerate(failed_requests, 1):
                    print(f"\n[요청 실패 {i}] {req['timestamp']}")
                    print(f"URL: {req['url']}")
                    print(f"방법: {req['method']}")
                    print(f"실패 사유: {req['failure']}")
            
            # WebSocket 관련 메시지 분석
            websocket_messages = [m for m in console_messages if 'websocket' in m['text'].lower() or 'vite' in m['text'].lower()]
            if websocket_messages:
                print(f"\n🌐 WebSocket/Vite 관련 메시지:")
                print(f"{'-'*60}")
                for msg in websocket_messages:
                    print(f"[{msg['timestamp']}] [{msg['type'].upper()}] {msg['text']}")
            
            # 브라우저 개발자 도구 열기
            await page.keyboard.press('F12')
            print(f"\n📌 개발자 도구가 열렸습니다. 5초간 수동 확인 가능...")
            await page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
        
        finally:
            await browser.close()
        
        # 최종 결과
        print(f"\n{'='*60}")
        if errors or failed_requests:
            print("❌ 콘솔 또는 네트워크에 문제가 있습니다.")
            return False
        elif warnings:
            print("⚠️  경고가 있습니다. 검토 필요.")
            return True
        else:
            print("✅ 모든 것이 정상입니다!")
            return True

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else "http://localhost:5173"
    success = asyncio.run(check_console_fresh_browser(url))
    sys.exit(0 if success else 1)