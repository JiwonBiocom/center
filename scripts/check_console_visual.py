#!/usr/bin/env python3
"""
Playwright를 사용하여 실제 브라우저 창을 띄우고 콘솔 메시지를 확인하는 스크립트
"""
import asyncio
import sys
from playwright.async_api import async_playwright
from datetime import datetime

async def check_console_messages_visual(url: str = "http://localhost:5173"):
    """실제 브라우저 창을 띄우고 콘솔 메시지를 수집하고 분석"""
    
    # 콘솔 메시지를 저장할 리스트
    console_messages = []
    errors = []
    warnings = []
    
    async with async_playwright() as p:
        # 브라우저 실행 (headless=False로 실제 창 표시)
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 콘솔 메시지 리스너 등록
        def handle_console(msg):
            message_type = msg.type
            text = msg.text
            location = msg.location
            
            message_data = {
                'type': message_type,
                'text': text,
                'url': location.get('url', ''),
                'line': location.get('lineNumber', 0),
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3]
            }
            
            console_messages.append(message_data)
            
            # 실시간으로 메시지 출력
            print(f"[{message_data['timestamp']}] [{message_type.upper()}] {text}")
            
            if message_type == 'error':
                errors.append(message_data)
            elif message_type == 'warning':
                warnings.append(message_data)
        
        page.on("console", handle_console)
        
        # 페이지 예외 처리
        def handle_page_error(err):
            error_data = {
                'type': 'pageerror',
                'text': str(err),
                'url': '',
                'line': 0,
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3]
            }
            errors.append(error_data)
            print(f"[{error_data['timestamp']}] [PAGEERROR] {str(err)}")
        
        page.on("pageerror", handle_page_error)
        
        # 네트워크 요청 실패 모니터링
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
        
        # WebSocket 에러 캐치를 위한 추가 리스너
        def handle_response(response):
            if response.status >= 400:
                print(f"[HTTP_ERROR] {response.status} {response.url}")
        
        page.on("response", handle_response)
        
        print(f"\n🔍 {url} 실제 브라우저에서 콘솔 메시지 확인 중...\n")
        print("📌 브라우저 창이 열립니다. 개발자 도구를 열어 콘솔을 함께 확인해보세요.")
        print("📌 15초 후 자동으로 결과를 출력합니다.")
        
        try:
            # 페이지 로드
            response = await page.goto(url, wait_until='networkidle', timeout=30000)
            
            if response and response.ok:
                print(f"✅ 페이지 로드 성공 (상태 코드: {response.status})")
            else:
                print(f"❌ 페이지 로드 실패 (상태 코드: {response.status if response else 'None'})")
            
            # 개발자 도구 열기 (선택적)
            await page.keyboard.press('F12')
            
            # 충분한 대기 시간 (WebSocket 연결 등을 위해)
            print("⏳ 15초간 대기하며 모든 콘솔 메시지를 수집합니다...")
            for i in range(15, 0, -1):
                print(f"⏳ {i}초 남음...", end='\r')
                await page.wait_for_timeout(1000)
            
            print("\n" + "="*60)
            print("📊 최종 콘솔 메시지 분석 결과")
            print("="*60)
            
            print(f"\n총 메시지 수: {len(console_messages)}")
            print(f"❌ 에러: {len(errors)}개")
            print(f"⚠️  경고: {len(warnings)}개")
            print(f"🔗 실패한 요청: {len(failed_requests)}개")
            print(f"ℹ️  정보/로그: {len([m for m in console_messages if m['type'] in ['log', 'info']])}개")
            print(f"🐛 디버그: {len([m for m in console_messages if m['type'] == 'debug'])}개\n")
            
            # 에러 메시지 상세 출력
            if errors:
                print(f"\n🚨 에러 메시지 상세:")
                print(f"{'-'*60}")
                for i, error in enumerate(errors, 1):
                    print(f"\n[에러 {i}] {error['timestamp']}")
                    print(f"타입: {error['type']}")
                    print(f"내용: {error['text']}")
                    if error['url']:
                        print(f"위치: {error['url']}:{error['line']}")
            
            # 경고 메시지 상세 출력
            if warnings:
                print(f"\n⚠️  경고 메시지 상세:")
                print(f"{'-'*60}")
                for i, warning in enumerate(warnings, 1):
                    print(f"\n[경고 {i}] {warning['timestamp']}")
                    print(f"내용: {warning['text']}")
                    if warning['url']:
                        print(f"위치: {warning['url']}:{warning['line']}")
            
            # 실패한 요청 출력
            if failed_requests:
                print(f"\n🔗 실패한 네트워크 요청:")
                print(f"{'-'*60}")
                for i, req in enumerate(failed_requests, 1):
                    print(f"\n[요청 실패 {i}] {req['timestamp']}")
                    print(f"URL: {req['url']}")
                    print(f"방법: {req['method']}")
                    print(f"실패 사유: {req['failure']}")
            
            # 모든 콘솔 메시지를 시간순으로 출력
            print(f"\n📝 모든 콘솔 메시지 (시간순):")
            print(f"{'-'*60}")
            for msg in console_messages:
                print(f"[{msg['timestamp']}] [{msg['type'].upper()}] {msg['text']}")
            
            # 브라우저를 5초 더 열어둠
            print(f"\n📌 브라우저를 5초 더 열어두고 수동으로 확인할 수 있습니다...")
            await page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"\n❌ 페이지 로드 중 오류 발생: {str(e)}")
        
        finally:
            await browser.close()
        
        # 최종 결과
        print(f"\n{'='*60}")
        if errors or failed_requests:
            print("❌ 콘솔에 에러 또는 네트워크 실패가 발견되었습니다.")
            return False
        elif warnings:
            print("⚠️  콘솔에 경고가 있습니다. 검토가 필요할 수 있습니다.")
            return True
        else:
            print("✅ 콘솔이 깨끗합니다!")
            return True

if __name__ == "__main__":
    # URL 파라미터 처리
    url = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else "http://localhost:5173"
    
    # 실행
    success = asyncio.run(check_console_messages_visual(url))
    sys.exit(0 if success else 1)