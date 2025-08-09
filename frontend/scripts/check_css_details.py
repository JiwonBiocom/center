#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import json

async def check_css_details():
    print("=== CSS 및 페이지 상세 분석 시작 ===\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 브라우저 창 표시
        context = await browser.new_context()
        page = await context.new_page()

        # 콘솔 메시지 수집
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))

        # 네트워크 요청 추적
        network_requests = []
        def track_request(request):
            if request.url.endswith('.css') or request.url.endswith('.js'):
                network_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "resource_type": request.resource_type
                })

        def track_response(response):
            for req in network_requests:
                if req["url"] == response.url:
                    req["status"] = response.status
                    req["status_text"] = response.status_text

        page.on("request", track_request)
        page.on("response", track_response)

        try:
            # 페이지 로드
            print("페이지 로드 중...")
            await page.goto("http://localhost:5173", wait_until="networkidle")
            await page.wait_for_timeout(2000)  # 추가 대기

            # 스크린샷 촬영
            await page.screenshot(path="/tmp/css_analysis.png")
            print("✅ 스크린샷 저장: /tmp/css_analysis.png")

            # HTML head 내용 확인
            head_content = await page.evaluate("""
                () => {
                    const head = document.head;
                    const links = Array.from(head.querySelectorAll('link[rel="stylesheet"]'));
                    const styles = Array.from(head.querySelectorAll('style'));

                    return {
                        links: links.map(link => ({
                            href: link.href,
                            rel: link.rel,
                            type: link.type || 'text/css'
                        })),
                        styles: styles.map(style => ({
                            textLength: style.textContent.length,
                            sample: style.textContent.substring(0, 100)
                        }))
                    };
                }
            """)

            print("\n=== HEAD 태그 내용 ===")
            print(f"스타일시트 링크: {len(head_content['links'])}개")
            for link in head_content['links']:
                print(f"  - {link['href']}")

            print(f"\n인라인 스타일: {len(head_content['styles'])}개")
            for i, style in enumerate(head_content['styles']):
                print(f"  - 스타일 {i+1}: {style['textLength']}자")

            # Body 요소 분석
            body_analysis = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    const withClasses = Array.from(elements).filter(el => el.className);
                    const tailwindClasses = Array.from(elements).filter(el =>
                        el.className && (
                            el.className.includes('bg-') ||
                            el.className.includes('text-') ||
                            el.className.includes('p-') ||
                            el.className.includes('m-') ||
                            el.className.includes('flex') ||
                            el.className.includes('grid')
                        )
                    );

                    // 샘플 요소들의 계산된 스타일
                    const sampleElements = [];
                    const samples = document.querySelectorAll('h1, button, .bg-blue-600, .text-white');
                    samples.forEach(el => {
                        const computed = window.getComputedStyle(el);
                        sampleElements.push({
                            tagName: el.tagName,
                            className: el.className,
                            backgroundColor: computed.backgroundColor,
                            color: computed.color,
                            padding: computed.padding,
                            display: computed.display
                        });
                    });

                    return {
                        totalElements: elements.length,
                        withClasses: withClasses.length,
                        tailwindClasses: tailwindClasses.length,
                        sampleElements: sampleElements
                    };
                }
            """)

            print("\n=== 요소 분석 ===")
            print(f"전체 요소: {body_analysis['totalElements']}개")
            print(f"클래스가 있는 요소: {body_analysis['withClasses']}개")
            print(f"Tailwind 클래스 요소: {body_analysis['tailwindClasses']}개")

            print("\n=== 샘플 요소들의 계산된 스타일 ===")
            for elem in body_analysis['sampleElements']:
                print(f"\n{elem['tagName']} (class: {elem['className']})")
                print(f"  배경색: {elem['backgroundColor']}")
                print(f"  글자색: {elem['color']}")
                print(f"  패딩: {elem['padding']}")
                print(f"  디스플레이: {elem['display']}")

            # index.css 내용 확인
            css_content = await page.evaluate("""
                async () => {
                    try {
                        const response = await fetch('/src/index.css');
                        const text = await response.text();
                        return {
                            status: response.status,
                            length: text.length,
                            sample: text.substring(0, 200)
                        };
                    } catch (error) {
                        return { error: error.message };
                    }
                }
            """)

            print("\n=== index.css 파일 확인 ===")
            if 'error' in css_content:
                print(f"❌ 에러: {css_content['error']}")
            else:
                print(f"상태: {css_content['status']}")
                print(f"크기: {css_content['length']}자")
                print(f"샘플:\n{css_content['sample']}")

            # 네트워크 요청 결과
            print("\n=== CSS/JS 파일 로드 상태 ===")
            for req in network_requests:
                status = req.get('status', 'pending')
                status_icon = "✅" if status == 200 else "❌"
                print(f"{status_icon} {req['resource_type']}: {req['url']} - {status}")

            # 콘솔 메시지
            if console_messages:
                print("\n=== 콘솔 메시지 ===")
                for msg in console_messages:
                    print(f"[{msg['type']}] {msg['text']}")
            else:
                print("\n✅ 콘솔 에러 없음")

            # 개발자 도구 열기 (수동 확인용)
            print("\n⚠️  브라우저 창이 열려있습니다. F12를 눌러 개발자 도구를 확인하세요.")
            print("확인 후 Enter를 눌러 종료하세요...")
            input()

        except Exception as e:
            print(f"\n❌ 에러 발생: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_css_details())
