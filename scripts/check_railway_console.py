#!/usr/bin/env python3
"""
Railway 배포 사이트의 콘솔 메시지 확인
Playwright를 사용하여 JavaScript 에러, 네트워크 에러 등을 감지
"""

import asyncio
import sys
from datetime import datetime
from playwright.async_api import async_playwright

async def check_console_messages(url: str):
    """웹사이트의 콘솔 메시지를 확인"""
    
    # 콘솔 메시지 수집
    console_messages = []
    network_errors = []
    js_errors = []
    
    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 콘솔 메시지 리스너
        page.on("console", lambda msg: console_messages.append({
            'type': msg.type,
            'text': msg.text,
            'location': msg.location
        }))
        
        # 페이지 에러 리스너
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        
        # 네트워크 실패 리스너
        page.on("requestfailed", lambda request: network_errors.append({
            'url': request.url,
            'failure': request.failure
        }))
        
        print(f"🔍 Checking console messages for: {url}")
        print("=" * 60)
        
        try:
            # 페이지 로드
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 응답 상태 확인
            print(f"\n📊 Response Status: {response.status}")
            
            # 추가 대기 (동적 콘텐츠 로딩)
            await page.wait_for_timeout(3000)
            
            # API 엔드포인트도 확인
            if not url.endswith('/api/'):
                api_urls = [
                    url.rstrip('/') + '/api/v1/health',
                    url.rstrip('/') + '/api/v1/customers'
                ]
                
                for api_url in api_urls:
                    try:
                        api_response = await page.evaluate(f'''
                            fetch("{api_url}")
                                .then(r => ({{ status: r.status, ok: r.ok }}))
                                .catch(e => ({{ error: e.message }}))
                        ''')
                        print(f"\n🌐 API Check - {api_url}:")
                        print(f"   Status: {api_response}")
                    except Exception as e:
                        print(f"   Error: {e}")
            
        except Exception as e:
            print(f"\n❌ Page load error: {e}")
        
        # 결과 분석
        print(f"\n📋 Console Messages Summary:")
        print(f"   Total messages: {len(console_messages)}")
        
        # 에러 메시지 필터링
        error_messages = [msg for msg in console_messages if msg['type'] in ['error', 'warning']]
        
        if error_messages:
            print(f"\n🚨 Errors and Warnings ({len(error_messages)}):")
            for msg in error_messages:
                print(f"   [{msg['type'].upper()}] {msg['text']}")
                if msg['location'].get('url'):
                    print(f"   Location: {msg['location']['url']}:{msg['location'].get('lineNumber', '?')}")
        
        if js_errors:
            print(f"\n💥 JavaScript Errors ({len(js_errors)}):")
            for error in js_errors:
                print(f"   {error}")
        
        if network_errors:
            print(f"\n🔌 Network Errors ({len(network_errors)}):")
            for error in network_errors:
                print(f"   URL: {error['url']}")
                print(f"   Failure: {error['failure']}")
        
        # 정상 로그도 일부 표시
        info_messages = [msg for msg in console_messages if msg['type'] == 'log'][:5]
        if info_messages:
            print(f"\n📝 Recent Log Messages (first 5):")
            for msg in info_messages:
                print(f"   {msg['text'][:100]}...")
        
        # 최종 판정
        print("\n" + "=" * 60)
        if not error_messages and not js_errors and not network_errors:
            print("✅ No console errors detected! The site appears to be running smoothly.")
        else:
            total_errors = len(error_messages) + len(js_errors) + len(network_errors)
            print(f"⚠️  Found {total_errors} total errors. Please review and fix them.")
        
        await browser.close()
        
        # 결과 반환
        return {
            'success': len(error_messages) + len(js_errors) + len(network_errors) == 0,
            'console_messages': console_messages,
            'error_count': len(error_messages),
            'js_error_count': len(js_errors),
            'network_error_count': len(network_errors)
        }

async def main():
    # Railway URL (환경변수나 인자로 받기)
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # 기본 Railway URL 패턴
        url = input("Enter Railway URL (e.g., https://your-app.up.railway.app): ").strip()
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    result = await check_console_messages(url)
    
    # 결과 저장
    report_file = f"console_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(f"Console Check Report for {url}\n")
        f.write(f"Generated at: {datetime.now().isoformat()}\n")
        f.write(f"Total Errors: {result['error_count'] + result['js_error_count'] + result['network_error_count']}\n")
        f.write("\nDetails:\n")
        for msg in result['console_messages']:
            f.write(f"[{msg['type']}] {msg['text']}\n")
    
    print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())