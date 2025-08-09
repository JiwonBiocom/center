#!/usr/bin/env python3
"""
최적화된 빌드 로딩 시간 측정
"""
import time
import asyncio
from playwright.async_api import async_playwright

async def measure_optimized_loading():
    """최적화된 버전의 로딩 시간 측정"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🚀 최적화된 빌드 성능 측정")
        print("=" * 50)
        
        # 네트워크 요청 추적
        js_files = []
        
        async def handle_response(response):
            if response.url.endswith('.js'):
                js_files.append({
                    'url': response.url.split('/')[-1],
                    'size': len(await response.body()) if response.ok else 0,
                    'status': response.status
                })
        
        page.on('response', handle_response)
        
        # 로딩 시간 측정
        start_time = time.time()
        
        try:
            # 빌드된 버전 접속
            await page.goto('http://localhost:4173/', wait_until='networkidle')
            
            # 로그인 폼이 나타날 때까지 대기
            await page.wait_for_selector('form', timeout=10000)
            
            total_time = time.time() - start_time
            
            print(f"✅ 초기 로딩 완료: {total_time:.2f}초")
            
            # JavaScript 파일 분석
            print(f"\n📦 로드된 JavaScript 파일:")
            print("-" * 50)
            
            total_size = 0
            for js in sorted(js_files, key=lambda x: x['size'], reverse=True):
                size_kb = js['size'] / 1024
                total_size += js['size']
                print(f"  {js['url'][:40]:40} {size_kb:8.1f} KB")
            
            print("-" * 50)
            print(f"  총 크기: {total_size / 1024:.1f} KB")
            
            # 로그인 후 대시보드 로딩 측정
            print(f"\n🔍 대시보드 페이지 로딩 테스트")
            print("-" * 50)
            
            # 테스트 계정으로 로그인
            await page.fill('input[type="email"]', 'admin@example.com')
            await page.fill('input[type="password"]', 'admin123')
            
            # 로그인 버튼 클릭 전 JS 파일 개수 저장
            before_login_js_count = len(js_files)
            
            dashboard_start = time.time()
            await page.click('button[type="submit"]')
            
            # 대시보드가 로드될 때까지 대기
            try:
                await page.wait_for_selector('h1', timeout=10000)
                dashboard_time = time.time() - dashboard_start
                
                # 추가로 로드된 JS 파일 확인
                new_js_files = js_files[before_login_js_count:]
                
                print(f"✅ 대시보드 로딩 시간: {dashboard_time:.2f}초")
                
                if new_js_files:
                    print(f"\n📥 추가로 로드된 파일:")
                    for js in new_js_files:
                        size_kb = js['size'] / 1024
                        print(f"  - {js['url'][:40]:40} {size_kb:8.1f} KB")
                
            except Exception as e:
                print(f"❌ 대시보드 로딩 실패: {e}")
            
            # 성능 평가
            print(f"\n💡 성능 평가:")
            print("-" * 50)
            
            if total_time < 1.5:
                print("⚡ 초기 로딩: 매우 빠름 (1.5초 미만)")
            elif total_time < 3:
                print("✅ 초기 로딩: 빠름 (3초 미만)")
            else:
                print("🔶 초기 로딩: 보통 (3초 이상)")
            
            # 최적화 효과 계산
            print(f"\n📈 최적화 효과:")
            print("-" * 50)
            print(f"이전 번들 크기: 1,277 KB")
            print(f"현재 초기 로드: {total_size / 1024:.1f} KB")
            print(f"절감율: {(1 - total_size / 1024 / 1277) * 100:.1f}%")
            
        except Exception as e:
            print(f"❌ 측정 실패: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(measure_optimized_loading())