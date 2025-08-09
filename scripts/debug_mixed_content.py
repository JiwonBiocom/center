#!/usr/bin/env python3
"""
Playwright를 사용한 Mixed Content 디버깅
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def debug_mixed_content():
    async with async_playwright() as p:
        # 브라우저 시작 (디버깅 모드)
        browser = await p.chromium.launch(
            headless=False,  # GUI 모드로 실행
            devtools=True    # 개발자 도구 자동 열기
        )
        
        context = await browser.new_context(
            # 캐시 완전 비활성화
            bypass_csp=True,
            ignore_https_errors=False
        )
        
        page = await context.new_page()
        
        # 콘솔 메시지 캡처
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }))
        
        # 네트워크 요청 캡처
        network_requests = []
        failed_requests = []
        
        def on_request(request):
            network_requests.append({
                "url": request.url,
                "method": request.method,
                "headers": request.headers,
                "initiator": request.post_data if request.method == "POST" else None
            })
            # HTTP URL 감지
            if request.url.startswith("http://") and "localhost" not in request.url:
                print(f"🚨 HTTP 요청 감지: {request.url}")
                print(f"   Method: {request.method}")
                print(f"   Headers: {json.dumps(dict(request.headers), indent=2)}")
        
        def on_request_failed(request):
            failed_requests.append({
                "url": request.url,
                "failure": request.failure,
                "method": request.method
            })
            print(f"❌ 요청 실패: {request.url}")
            print(f"   원인: {request.failure}")
        
        page.on("request", on_request)
        page.on("requestfailed", on_request_failed)
        
        # 페이지 로드
        print("🌐 페이지 로딩: https://center-ten.vercel.app")
        response = await page.goto("https://center-ten.vercel.app", wait_until="networkidle")
        
        print(f"\n📊 초기 로드 상태: {response.status}")
        
        # 5초 대기 (추가 요청 캡처)
        await page.wait_for_timeout(5000)
        
        # 로그인 시도
        print("\n🔐 로그인 시도...")
        await page.fill('input[type="email"]', 'admin@aibio.kr')
        await page.fill('input[type="password"]', 'admin123')
        await page.click('button[type="submit"]')
        
        # 로그인 후 대기
        await page.wait_for_timeout(5000)
        
        # 결과 분석
        print("\n📋 분석 결과:")
        print(f"총 요청 수: {len(network_requests)}")
        print(f"실패한 요청 수: {len(failed_requests)}")
        
        # HTTP 요청 찾기
        http_requests = [req for req in network_requests if req["url"].startswith("http://") and "localhost" not in req["url"]]
        if http_requests:
            print(f"\n🚨 HTTP 요청 발견 ({len(http_requests)}개):")
            for req in http_requests[:5]:  # 최대 5개만
                print(f"  - {req['method']} {req['url']}")
        
        # 콘솔 에러 확인
        errors = [msg for msg in console_messages if msg["type"] == "error"]
        if errors:
            print(f"\n❌ 콘솔 에러 ({len(errors)}개):")
            for err in errors[:5]:  # 최대 5개만
                print(f"  - {err['text']}")
                if err['location']:
                    print(f"    위치: {err['location']}")
        
        # 현재 로드된 스크립트 확인
        scripts = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script[src]'));
                return scripts.map(s => ({
                    src: s.src,
                    type: s.type || 'text/javascript'
                }));
            }
        """)
        
        print("\n📜 로드된 스크립트:")
        for script in scripts:
            print(f"  - {script['src']}")
        
        # API URL 환경변수 확인
        api_config = await page.evaluate("""
            () => {
                // 전역 객체에서 API 관련 설정 찾기
                const config = {};
                
                // import.meta.env 확인 (Vite)
                if (typeof import !== 'undefined' && import.meta && import.meta.env) {
                    config.VITE_API_URL = import.meta.env.VITE_API_URL;
                    config.MODE = import.meta.env.MODE;
                }
                
                // window 객체에서 API 관련 찾기
                for (const key in window) {
                    if (key.toLowerCase().includes('api') || key.toLowerCase().includes('url')) {
                        config[key] = window[key];
                    }
                }
                
                return config;
            }
        """)
        
        print("\n🔧 API 설정:")
        print(json.dumps(api_config, indent=2))
        
        # 특정 요청의 Initiator 추적
        if failed_requests:
            print("\n🔍 실패한 요청 상세 분석:")
            for req in failed_requests[:3]:
                print(f"\nURL: {req['url']}")
                print(f"Method: {req['method']}")
                print(f"Failure: {req['failure']}")
        
        # 스크린샷 저장
        await page.screenshot(path="/tmp/mixed-content-debug.png", full_page=True)
        print("\n📸 스크린샷 저장: /tmp/mixed-content-debug.png")
        
        # 브라우저는 열어둠 (수동 검사용)
        print("\n⏸️  브라우저를 열어두었습니다. 수동으로 검사하세요.")
        print("완료하려면 Enter를 누르세요...")
        input()
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_mixed_content())