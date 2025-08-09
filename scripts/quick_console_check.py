#!/usr/bin/env python3
"""
빠른 콘솔 체크 - Railway나 로컬 서버 모두 가능
"""

import asyncio
from playwright.async_api import async_playwright

async def quick_check(url="http://localhost:5173"):
    """빠른 콘솔 체크"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 에러 수집
        errors = []
        warnings = []
        
        # 리스너 설정
        page.on("console", lambda msg: (
            errors.append(msg.text) if msg.type == "error" 
            else warnings.append(msg.text) if msg.type == "warning"
            else None
        ))
        
        page.on("pageerror", lambda err: errors.append(f"JS Error: {err}"))
        
        print(f"🔍 Checking: {url}")
        
        try:
            # 페이지 로드
            response = await page.goto(url, timeout=30000)
            await page.wait_for_timeout(2000)  # 동적 콘텐츠 대기
            
            print(f"✅ Status: {response.status}")
            
            # API 체크
            if "localhost" not in url and "railway" in url:
                api_health = await page.evaluate('''
                    fetch("/api/v1/health")
                        .then(r => r.status)
                        .catch(() => "Failed")
                ''')
                print(f"🌐 API Health: {api_health}")
            
            # 결과 출력
            print(f"\n📊 Results:")
            print(f"   Errors: {len(errors)}")
            print(f"   Warnings: {len(warnings)}")
            
            if errors:
                print("\n🚨 Errors:")
                for err in errors[:5]:  # 처음 5개만
                    print(f"   - {err[:100]}...")
            
            if warnings:
                print("\n⚠️  Warnings:")
                for warn in warnings[:3]:  # 처음 3개만
                    print(f"   - {warn[:100]}...")
            
            if not errors and not warnings:
                print("\n✅ Console is clean! No errors or warnings.")
            
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
        
        await browser.close()

if __name__ == "__main__":
    import sys
    
    # URL 받기
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Usage: python quick_console_check.py <URL>")
        print("Example: python quick_console_check.py https://your-app.railway.app")
        url = input("Enter URL (or press Enter for localhost:5173): ").strip() or "http://localhost:5173"
    
    asyncio.run(quick_check(url))