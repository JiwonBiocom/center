#!/usr/bin/env python3
"""
Vercel 최적화된 버전 성능 측정
"""
import time
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

VERCEL_URL = "https://center-ten.vercel.app"

async def measure_optimized_performance():
    """최적화된 Vercel 버전의 성능 측정"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 실제로 보기
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🚀 Vercel 최적화 버전 성능 측정")
        print(f"URL: {VERCEL_URL}")
        print(f"시간: {datetime.now()}")
        print("=" * 60)
        
        # JavaScript 파일 추적
        js_files = []
        
        async def handle_response(response):
            if response.url.endswith('.js') and response.status == 200:
                js_files.append({
                    'url': response.url.split('/')[-1],
                    'size': len(await response.body()),
                    'time': time.time()
                })
        
        page.on('response', handle_response)
        
        # 1. 초기 로딩 측정
        print("\n📱 대시보드 로딩 중...")
        start_time = time.time()
        
        try:
            await page.goto(VERCEL_URL, wait_until='networkidle', timeout=30000)
            initial_load_time = time.time() - start_time
            
            print(f"✅ 초기 로딩 완료: {initial_load_time:.2f}초")
            
            # 로그인 폼 대기
            await page.wait_for_selector('form', timeout=10000)
            
            # 초기 로드된 JS 파일 분석
            initial_js_count = len(js_files)
            total_initial_size = sum(f['size'] for f in js_files)
            
            print(f"\n📦 초기 로드된 JavaScript:")
            print(f"  - 파일 수: {initial_js_count}개")
            print(f"  - 총 크기: {total_initial_size / 1024:.1f} KB")
            
            # 주요 청크 표시
            for js in sorted(js_files, key=lambda x: x['size'], reverse=True)[:5]:
                print(f"    • {js['url'][:40]:40} {js['size'] / 1024:8.1f} KB")
            
            # 스크린샷
            await page.screenshot(path='vercel_optimized_login.png')
            
            # 2. 로그인 후 대시보드 측정
            print(f"\n🔐 로그인 중...")
            await page.fill('input[type="email"]', 'admin@example.com')
            await page.fill('input[type="password"]', 'admin123')
            
            dashboard_start = time.time()
            await page.click('button[type="submit"]')
            
            # 대시보드 로드 대기
            try:
                await page.wait_for_selector('h1', timeout=10000)
                dashboard_load_time = time.time() - dashboard_start
                
                # 추가로 로드된 JS 파일
                new_js_files = js_files[initial_js_count:]
                
                print(f"\n✅ 대시보드 로딩 완료: {dashboard_load_time:.2f}초")
                
                if new_js_files:
                    additional_size = sum(f['size'] for f in new_js_files)
                    print(f"\n📥 추가 로드된 JavaScript:")
                    print(f"  - 파일 수: {len(new_js_files)}개")
                    print(f"  - 추가 크기: {additional_size / 1024:.1f} KB")
                    
                    for js in new_js_files[:5]:
                        print(f"    • {js['url'][:40]:40} {js['size'] / 1024:8.1f} KB")
                
                # 대시보드 스크린샷
                await page.screenshot(path='vercel_optimized_dashboard.png')
                
            except Exception as e:
                print(f"❌ 대시보드 로딩 실패: {e}")
            
            # 3. 성능 분석
            print(f"\n📊 성능 분석:")
            print("=" * 60)
            
            total_time = initial_load_time + (dashboard_load_time if 'dashboard_load_time' in locals() else 0)
            print(f"전체 로딩 시간: {total_time:.2f}초")
            
            if initial_load_time < 2:
                print("⚡ 초기 로딩: 매우 빠름 (2초 미만)")
            elif initial_load_time < 3:
                print("✅ 초기 로딩: 빠름 (3초 미만)")
            elif initial_load_time < 5:
                print("🔶 초기 로딩: 보통 (5초 미만)")
            else:
                print("❌ 초기 로딩: 느림 (5초 이상)")
            
            # 최적화 효과
            print(f"\n📈 최적화 효과:")
            print(f"  - 이전 초기 번들: 1,277 KB")
            print(f"  - 현재 초기 로드: {total_initial_size / 1024:.1f} KB")
            print(f"  - 크기 감소율: {(1 - total_initial_size / 1024 / 1277) * 100:.1f}%")
            print(f"  - 예상 로딩 시간 단축: {(5 - initial_load_time):.1f}초")
            
        except Exception as e:
            print(f"❌ 측정 실패: {e}")
        
        input("\n브라우저를 닫으려면 Enter를 누르세요...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(measure_optimized_performance())