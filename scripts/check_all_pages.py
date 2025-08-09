#!/usr/bin/env python3
"""
전체 페이지 상태 점검 스크립트
모든 주요 페이지의 콘솔 에러와 API 호출 상태를 체크
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import json

# 체크할 페이지 목록
PAGES_TO_CHECK = [
    {"path": "/", "name": "대시보드"},
    {"path": "/customers", "name": "고객관리"},
    {"path": "/services", "name": "서비스관리"},
    {"path": "/payments", "name": "결제관리"},
    {"path": "/packages", "name": "패키지관리"},
    {"path": "/reports", "name": "리포트"},
    {"path": "/notifications", "name": "알림"},
    {"path": "/leads", "name": "유입고객"},
    {"path": "/settings", "name": "설정"},
]

async def check_all_pages():
    """모든 페이지 상태 체크"""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": "https://center-ten.vercel.app",
        "pages": {},
        "summary": {
            "total_pages": len(PAGES_TO_CHECK),
            "healthy_pages": 0,
            "pages_with_errors": 0,
            "pages_with_warnings": 0,
            "api_errors": []
        }
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("🔍 AIBIO 센터 전체 페이지 상태 점검")
        print("="*60)
        
        # 1. 로그인
        print("\n1️⃣ 로그인 중...")
        await page.goto("https://center-ten.vercel.app/login")
        await page.fill('input[type="email"]', "admin@aibio.com")
        await page.fill('input[type="password"]', "admin123")
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/", timeout=10000)
        print("   ✅ 로그인 성공")
        
        # 2. 각 페이지 체크
        print("\n2️⃣ 페이지별 상태 체크:")
        print("-"*60)
        
        for page_info in PAGES_TO_CHECK:
            path = page_info["path"]
            name = page_info["name"]
            
            # 콘솔 메시지 초기화
            console_messages = []
            network_errors = []
            
            # 콘솔 리스너 설정
            def handle_console(msg):
                console_messages.append({
                    "type": msg.type,
                    "text": msg.text,
                    "location": msg.location if hasattr(msg, 'location') else None
                })
            
            # 네트워크 실패 리스너
            def handle_request_failed(request):
                network_errors.append({
                    "url": request.url,
                    "failure": request.failure
                })
            
            page.on("console", handle_console)
            page.on("requestfailed", handle_request_failed)
            
            print(f"\n📄 {name} ({path})")
            
            try:
                # 페이지 로드
                response = await page.goto(f"https://center-ten.vercel.app{path}", wait_until="networkidle")
                await page.wait_for_timeout(2000)  # 동적 콘텐츠 대기
                
                # 현재 URL 확인 (리다이렉트 체크)
                current_url = page.url
                redirected = not current_url.endswith(path) and path != "/"
                
                # 에러/경고 분석
                errors = [msg for msg in console_messages if msg["type"] == "error"]
                warnings = [msg for msg in console_messages if msg["type"] == "warning"]
                api_errors = [msg for msg in console_messages if "404" in msg["text"] or "500" in msg["text"]]
                
                # 결과 저장
                page_result = {
                    "status": "healthy" if not errors else "error",
                    "response_code": response.status if response else None,
                    "redirected": redirected,
                    "current_url": current_url,
                    "console_errors": len(errors),
                    "console_warnings": len(warnings),
                    "network_errors": len(network_errors),
                    "api_errors": len(api_errors),
                    "error_details": errors[:3] if errors else [],  # 처음 3개만
                    "api_error_details": api_errors[:3] if api_errors else []
                }
                
                results["pages"][path] = page_result
                
                # 출력
                status_icon = "✅" if not errors else "❌"
                print(f"   상태: {status_icon} {page_result['status'].upper()}")
                print(f"   HTTP: {page_result['response_code']}")
                
                if redirected:
                    print(f"   ⚠️ 리다이렉트됨: {current_url}")
                
                if errors:
                    print(f"   🚨 에러: {len(errors)}개")
                    for err in errors[:2]:
                        print(f"      - {err['text'][:100]}...")
                
                if api_errors:
                    print(f"   🔴 API 에러:")
                    for err in api_errors[:2]:
                        print(f"      - {err['text'][:100]}...")
                
                if warnings:
                    print(f"   ⚠️ 경고: {len(warnings)}개")
                
                # 요약 업데이트
                if not errors:
                    results["summary"]["healthy_pages"] += 1
                else:
                    results["summary"]["pages_with_errors"] += 1
                
                if warnings:
                    results["summary"]["pages_with_warnings"] += 1
                
                if api_errors:
                    for err in api_errors:
                        if err["text"] not in results["summary"]["api_errors"]:
                            results["summary"]["api_errors"].append(err["text"])
                
            except Exception as e:
                print(f"   ❌ 페이지 로드 실패: {e}")
                results["pages"][path] = {
                    "status": "failed",
                    "error": str(e)
                }
                results["summary"]["pages_with_errors"] += 1
            
            # 리스너 제거
            page.remove_listener("console", handle_console)
            page.remove_listener("requestfailed", handle_request_failed)
        
        # 3. 전체 요약
        print("\n"+"="*60)
        print("📊 전체 요약:")
        print(f"   총 페이지: {results['summary']['total_pages']}개")
        print(f"   정상: {results['summary']['healthy_pages']}개")
        print(f"   에러: {results['summary']['pages_with_errors']}개")
        print(f"   경고: {results['summary']['pages_with_warnings']}개")
        
        if results["summary"]["api_errors"]:
            print(f"\n🔴 발견된 API 에러:")
            for err in results["summary"]["api_errors"]:
                print(f"   - {err}")
        
        # 4. 결과 저장
        report_file = f"page_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📁 상세 리포트 저장: {report_file}")
        
        await browser.close()
        
        # 5. 개발 계획 제안
        print("\n"+"="*60)
        print("🛠️ 개발 계획 제안:")
        
        if results["summary"]["pages_with_errors"] == 0:
            print("   ✅ 모든 페이지가 정상 작동 중입니다!")
        else:
            print("\n   우선순위별 작업 목록:")
            priority = 1
            
            # API 에러가 있는 페이지
            for path, info in results["pages"].items():
                if info.get("api_errors", 0) > 0:
                    page_name = next(p["name"] for p in PAGES_TO_CHECK if p["path"] == path)
                    print(f"   {priority}. [{page_name}] API 엔드포인트 수정")
                    priority += 1
            
            # 콘솔 에러가 있는 페이지
            for path, info in results["pages"].items():
                if info.get("console_errors", 0) > 0 and info.get("api_errors", 0) == 0:
                    page_name = next(p["name"] for p in PAGES_TO_CHECK if p["path"] == path)
                    print(f"   {priority}. [{page_name}] 콘솔 에러 해결")
                    priority += 1
        
        return results

if __name__ == "__main__":
    asyncio.run(check_all_pages())