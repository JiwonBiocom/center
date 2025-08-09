#!/usr/bin/env python3
"""
Playwright를 통한 웹 애플리케이션 콘솔 메시지 검증
모든 메뉴에서 JavaScript 에러, 네트워크 에러 확인
"""

import asyncio
import sys
from playwright.async_api import async_playwright
import json
from datetime import datetime

class WebAppChecker:
    def __init__(self, base_url="https://center-git-refactor-phase-1-utilities-vibetjs-projects.vercel.app"):
        self.base_url = base_url
        self.console_messages = []
        self.network_errors = []
        self.js_errors = []
        
    async def check_page(self, page, url, page_name):
        """개별 페이지 체크"""
        print(f"\n📍 {page_name} 페이지 검증 중...")
        
        # 콘솔 메시지 수집
        page_console_messages = []
        page_network_errors = []
        page_js_errors = []
        
        # 콘솔 이벤트 리스너
        def handle_console(msg):
            message_data = {
                'page': page_name,
                'type': msg.type,
                'text': msg.text,
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
            page_console_messages.append(message_data)
            
            if msg.type == 'error':
                page_js_errors.append(message_data)
                print(f"   ❌ JS Error: {msg.text}")
            elif msg.type == 'warning':
                print(f"   ⚠️  Warning: {msg.text}")
            
        # 네트워크 실패 리스너
        def handle_response(response):
            if response.status >= 400:
                error_data = {
                    'page': page_name,
                    'url': response.url,
                    'status': response.status,
                    'method': response.request.method,
                    'timestamp': datetime.now().isoformat()
                }
                page_network_errors.append(error_data)
                print(f"   🌐 Network Error: {response.status} {response.url}")
        
        # 이벤트 리스너 등록
        page.on('console', handle_console)
        page.on('response', handle_response)
        
        try:
            # 페이지 로드
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 페이지가 완전히 로드될 때까지 대기
            await page.wait_for_timeout(3000)
            
            # 페이지 제목 확인
            title = await page.title()
            print(f"   📄 페이지 제목: {title}")
            
            # 기본 요소들이 로드되었는지 확인
            try:
                # 로딩 스피너가 사라질 때까지 대기
                await page.wait_for_selector('[data-testid="loading"]', state='detached', timeout=5000)
            except:
                pass  # 로딩 스피너가 없을 수도 있음
            
            # 메인 컨텐츠 영역 확인
            main_content = await page.query_selector('main, [role="main"], .main-content, #root > div')
            if main_content:
                print(f"   ✅ 메인 컨텐츠 로드 완료")
            else:
                print(f"   ⚠️  메인 컨텐츠 찾을 수 없음")
            
            # 추가 대기 (비동기 컴포넌트 로딩)
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            error_data = {
                'page': page_name,
                'error': str(e),
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
            page_js_errors.append(error_data)
            print(f"   ❌ 페이지 로드 실패: {e}")
        
        # 결과 저장
        self.console_messages.extend(page_console_messages)
        self.network_errors.extend(page_network_errors)
        self.js_errors.extend(page_js_errors)
        
        return {
            'page': page_name,
            'url': url,
            'console_messages': len(page_console_messages),
            'network_errors': len(page_network_errors),
            'js_errors': len(page_js_errors),
            'status': 'success' if len(page_js_errors) == 0 and len(page_network_errors) == 0 else 'has_issues'
        }
    
    async def run_full_check(self):
        """전체 애플리케이션 체크"""
        print("🎭 Playwright 웹 애플리케이션 검증 시작")
        print(f"🌐 대상 URL: {self.base_url}")
        print("=" * 60)
        
        async with async_playwright() as p:
            # 브라우저 실행
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 체크할 페이지들 정의
            pages_to_check = [
                ('메인 대시보드', '/'),
                ('고객 관리', '/customers'),
                ('결제 관리', '/payments'),
                ('예약 관리', '/reservations'),
                ('서비스 관리', '/services'),
                ('패키지 관리', '/packages'),
                ('리드 관리', '/leads'),
                ('키트 관리', '/kits'),
                ('설정', '/settings'),
                ('통계', '/analytics'),
            ]
            
            results = []
            
            # 각 페이지 체크
            for page_name, path in pages_to_check:
                url = f"{self.base_url}{path}"
                result = await self.check_page(page, url, page_name)
                results.append(result)
                
                # 페이지 간 간격
                await page.wait_for_timeout(1000)
            
            await browser.close()
            
            # 결과 분석 및 출력
            self.print_summary(results)
            return results
    
    def print_summary(self, results):
        """결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📊 웹 애플리케이션 검증 결과 요약")
        print("=" * 60)
        
        total_pages = len(results)
        success_pages = len([r for r in results if r['status'] == 'success'])
        
        print(f"📄 총 페이지: {total_pages}개")
        print(f"✅ 성공: {success_pages}개")
        print(f"❌ 문제 있음: {total_pages - success_pages}개")
        
        # 상세 결과
        print(f"\n📋 페이지별 상세 결과:")
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"  {status_icon} {result['page']}: JS에러 {result['js_errors']}개, 네트워크에러 {result['network_errors']}개")
        
        # JavaScript 에러 상세
        if self.js_errors:
            print(f"\n🔴 JavaScript 에러 상세 ({len(self.js_errors)}개):")
            for error in self.js_errors:
                print(f"  • [{error['page']}] {error.get('text', error.get('error', 'Unknown error'))}")
        
        # 네트워크 에러 상세
        if self.network_errors:
            print(f"\n🌐 네트워크 에러 상세 ({len(self.network_errors)}개):")
            for error in self.network_errors:
                print(f"  • [{error['page']}] {error['status']} {error['url']}")
        
        # 전체 평가
        total_errors = len(self.js_errors) + len(self.network_errors)
        if total_errors == 0:
            print(f"\n🎉 축하합니다! 모든 페이지가 깨끗하게 작동합니다!")
        else:
            print(f"\n⚠️  총 {total_errors}개의 문제가 발견되었습니다.")
        
        # 결과를 JSON 파일로 저장
        report = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'summary': {
                'total_pages': total_pages,
                'success_pages': success_pages,
                'total_js_errors': len(self.js_errors),
                'total_network_errors': len(self.network_errors)
            },
            'page_results': results,
            'js_errors': self.js_errors,
            'network_errors': self.network_errors,
            'console_messages': self.console_messages
        }
        
        report_file = f"/Users/vibetj/coding/center/web_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 상세 리포트 저장: {report_file}")

async def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://center-git-refactor-phase-1-utilities-vibetjs-projects.vercel.app"
    
    checker = WebAppChecker(url)
    await checker.run_full_check()

if __name__ == "__main__":
    asyncio.run(main())