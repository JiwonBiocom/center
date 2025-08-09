#!/usr/bin/env python3
"""
각 메뉴별 상세 콘솔 메시지 및 네트워크 에러 분석
"""

import asyncio
import json
from playwright.async_api import async_playwright
from datetime import datetime

class DetailedMenuAnalyzer:
    def __init__(self, base_url="https://center-ten.vercel.app"):
        self.base_url = base_url
        self.analysis_results = {}
        
    async def analyze_menu(self, page, menu_name, path):
        """개별 메뉴 상세 분석"""
        print(f"\n🔍 === {menu_name} 메뉴 분석 ===")
        
        # 수집 데이터 초기화
        console_messages = []
        network_errors = []
        network_requests = []
        api_calls = []
        
        # 콘솔 메시지 수집
        def handle_console(msg):
            message_data = {
                'type': msg.type,
                'text': msg.text,
                'location': msg.location if hasattr(msg, 'location') else None,
                'timestamp': datetime.now().isoformat()
            }
            console_messages.append(message_data)
            
            if msg.type == 'error':
                print(f"   ❌ JS Error: {msg.text}")
            elif msg.type == 'warning':
                print(f"   ⚠️  Warning: {msg.text}")
            elif msg.type == 'info' and 'API' in msg.text:
                print(f"   ℹ️  API Info: {msg.text}")
        
        # 네트워크 요청 수집
        def handle_request(request):
            request_data = {
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers),
                'timestamp': datetime.now().isoformat()
            }
            network_requests.append(request_data)
            
            # API 호출 식별
            if '/api/' in request.url:
                api_calls.append(request_data)
                print(f"   🌐 API Call: {request.method} {request.url}")
        
        # 네트워크 응답 수집
        def handle_response(response):
            if response.status >= 400:
                error_data = {
                    'url': response.url,
                    'status': response.status,
                    'method': response.request.method,
                    'headers': dict(response.headers),
                    'timestamp': datetime.now().isoformat()
                }
                network_errors.append(error_data)
                print(f"   🚨 Network Error: {response.status} {response.url}")
            elif '/api/' in response.url:
                print(f"   ✅ API Success: {response.status} {response.url}")
        
        # 이벤트 리스너 등록
        page.on('console', handle_console)
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        try:
            # 페이지 로드
            url = f"{self.base_url}{path}"
            print(f"📍 URL: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(5000)
            
            # 페이지 제목 확인
            title = await page.title()
            print(f"📄 페이지 제목: {title}")
            
            # 로딩 상태 확인
            loading_indicators = await page.query_selector_all('[data-testid*="loading"], .loading, .spinner')
            if loading_indicators:
                print(f"⏳ 로딩 인디케이터 발견: {len(loading_indicators)}개")
                await page.wait_for_timeout(3000)
            
            # 에러 메시지 확인
            error_messages = await page.query_selector_all('.error, [role="alert"], .alert-error')
            if error_messages:
                for i, error in enumerate(error_messages):
                    text = await error.text_content()
                    print(f"🔴 UI Error {i+1}: {text}")
            
            # 데이터 테이블 확인
            tables = await page.query_selector_all('table, .table, [role="table"]')
            if tables:
                print(f"📊 테이블 발견: {len(tables)}개")
                for i, table in enumerate(tables):
                    rows = await table.query_selector_all('tr, .table-row')
                    print(f"   테이블 {i+1}: {len(rows)}행")
            
            # 빈 상태 메시지 확인
            empty_states = await page.query_selector_all('.empty-state, .no-data, .empty')
            if empty_states:
                for i, empty in enumerate(empty_states):
                    text = await empty.text_content()
                    print(f"📭 빈 상태 {i+1}: {text}")
            
            # 추가 대기 (비동기 요청 완료)
            await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"❌ 페이지 분석 실패: {e}")
            console_messages.append({
                'type': 'error',
                'text': f"Page analysis failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            })
        
        # 결과 정리
        result = {
            'menu': menu_name,
            'path': path,
            'url': f"{self.base_url}{path}",
            'title': title if 'title' in locals() else 'Unknown',
            'console_messages': console_messages,
            'network_errors': network_errors,
            'network_requests': network_requests,
            'api_calls': api_calls,
            'summary': {
                'total_console_messages': len(console_messages),
                'js_errors': len([m for m in console_messages if m['type'] == 'error']),
                'warnings': len([m for m in console_messages if m['type'] == 'warning']),
                'network_errors': len(network_errors),
                'api_calls': len(api_calls),
                'failed_api_calls': len([e for e in network_errors if '/api/' in e['url']])
            }
        }
        
        self.analysis_results[menu_name] = result
        
        print(f"📊 {menu_name} 요약:")
        print(f"   JS 에러: {result['summary']['js_errors']}개")
        print(f"   네트워크 에러: {result['summary']['network_errors']}개")
        print(f"   API 호출: {result['summary']['api_calls']}개")
        print(f"   실패한 API: {result['summary']['failed_api_calls']}개")
        
        return result
    
    async def run_full_analysis(self):
        """전체 메뉴 분석 실행"""
        print("🎭 상세 메뉴별 분석 시작")
        print(f"🌐 대상 URL: {self.base_url}")
        print("=" * 80)
        
        # 분석할 메뉴들
        menus = [
            ('대시보드', '/'),
            ('고객 관리', '/customers'),
            ('결제 관리', '/payments'),
            ('예약 관리', '/reservations'),
            ('서비스 관리', '/services'),
            ('패키지 관리', '/packages'),
            ('리드 관리', '/leads'),
            ('키트 관리', '/kits'),
            ('설정', '/settings'),
            ('통계', '/reports'),
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 각 메뉴 분석
            for menu_name, path in menus:
                await self.analyze_menu(page, menu_name, path)
                await page.wait_for_timeout(2000)  # 메뉴 간 간격
            
            await browser.close()
        
        # 결과 요약 및 저장
        self.generate_summary_report()
        return self.analysis_results
    
    def generate_summary_report(self):
        """요약 리포트 생성"""
        print("\n" + "=" * 80)
        print("📋 전체 분석 결과 요약")
        print("=" * 80)
        
        total_menus = len(self.analysis_results)
        clean_menus = 0
        problematic_menus = []
        
        for menu_name, result in self.analysis_results.items():
            summary = result['summary']
            if summary['js_errors'] == 0 and summary['failed_api_calls'] == 0:
                clean_menus += 1
            else:
                problematic_menus.append(menu_name)
        
        print(f"📊 전체 메뉴: {total_menus}개")
        print(f"✅ 정상 메뉴: {clean_menus}개")
        print(f"❌ 문제 메뉴: {len(problematic_menus)}개")
        
        if problematic_menus:
            print(f"\n🚨 문제 발견 메뉴들:")
            for menu in problematic_menus:
                result = self.analysis_results[menu]
                summary = result['summary']
                print(f"   • {menu}: JS에러 {summary['js_errors']}개, API실패 {summary['failed_api_calls']}개")
        
        # API 에러 패턴 분석
        self.analyze_api_error_patterns()
        
        # 결과를 JSON 파일로 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"/Users/vibetj/coding/center/detailed_menu_analysis_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 상세 리포트 저장: {report_file}")
    
    def analyze_api_error_patterns(self):
        """API 에러 패턴 분석"""
        print(f"\n🔍 API 에러 패턴 분석:")
        
        all_api_errors = []
        for result in self.analysis_results.values():
            all_api_errors.extend(result['network_errors'])
        
        if not all_api_errors:
            print("   ✅ API 에러 없음")
            return
        
        # 상태 코드별 분류
        error_by_status = {}
        for error in all_api_errors:
            status = error['status']
            if status not in error_by_status:
                error_by_status[status] = []
            error_by_status[status].append(error['url'])
        
        for status, urls in error_by_status.items():
            print(f"   🚨 {status} 에러: {len(urls)}개")
            for url in set(urls)[:3]:  # 중복 제거하고 처음 3개만
                print(f"      • {url}")
            if len(set(urls)) > 3:
                print(f"      • ... 및 {len(set(urls)) - 3}개 더")

async def main():
    analyzer = DetailedMenuAnalyzer()
    await analyzer.run_full_analysis()

if __name__ == "__main__":
    asyncio.run(main())