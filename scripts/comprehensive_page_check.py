#!/usr/bin/env python3
"""
종합적인 페이지 상태 체크 및 개발 계획 수립
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import json

PAGES = [
    {"path": "/", "name": "대시보드", "priority": 1},
    {"path": "/customers", "name": "고객관리", "priority": 1},
    {"path": "/services", "name": "서비스관리", "priority": 1},
    {"path": "/payments", "name": "결제관리", "priority": 1},
    {"path": "/packages", "name": "패키지관리", "priority": 2},
    {"path": "/reports", "name": "리포트", "priority": 2},
    {"path": "/notifications", "name": "알림", "priority": 3},
    {"path": "/leads", "name": "유입고객", "priority": 2},
    {"path": "/settings", "name": "설정", "priority": 3},
]

async def comprehensive_check():
    results = {
        "timestamp": datetime.now().isoformat(),
        "pages": {},
        "issues": [],
        "development_plan": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🔍 AIBIO 센터 종합 페이지 점검")
        print("="*70)
        
        # 1. 로그인
        print("\n1️⃣ 로그인...")
        await page.goto("https://center-ten.vercel.app/login")
        await page.fill('input[type="email"]', "admin@aibio.com")
        await page.fill('input[type="password"]', "admin123")
        await page.click('button[type="submit"]')
        await page.wait_for_url("https://center-ten.vercel.app/", timeout=10000)
        
        # 토큰 확인
        token = await page.evaluate('''() => {
            return localStorage.getItem('token');
        }''')
        print(f"   ✅ 로그인 성공 (토큰: {'있음' if token else '없음'})")
        
        # 2. 각 페이지 체크
        print("\n2️⃣ 페이지별 상세 체크:")
        print("-"*70)
        
        for page_info in PAGES:
            path = page_info["path"]
            name = page_info["name"]
            priority = page_info["priority"]
            
            # 메시지 초기화
            console_messages = []
            network_failures = []
            api_calls = []
            
            # 리스너 설정
            def handle_console(msg):
                console_messages.append({
                    "type": msg.type,
                    "text": msg.text
                })
            
            def handle_request(request):
                if "/api/v1/" in request.url:
                    api_calls.append({
                        "url": request.url,
                        "method": request.method
                    })
            
            def handle_response(response):
                if "/api/v1/" in response.url and response.status >= 400:
                    network_failures.append({
                        "url": response.url,
                        "status": response.status
                    })
            
            page.on("console", handle_console)
            page.on("request", handle_request)
            page.on("response", handle_response)
            
            print(f"\n📄 {name} ({path})")
            
            try:
                # 페이지 로드
                await page.goto(f"https://center-ten.vercel.app{path}", wait_until="networkidle")
                await page.wait_for_timeout(2000)
                
                # 현재 URL
                current_url = page.url
                
                # 분석
                errors = [msg for msg in console_messages if msg["type"] == "error"]
                warnings = [msg for msg in console_messages if msg["type"] == "warning"]
                
                # 404 에러 추출
                api_404s = [nf for nf in network_failures if nf["status"] == 404]
                api_500s = [nf for nf in network_failures if nf["status"] >= 500]
                
                # 결과 저장
                page_result = {
                    "name": name,
                    "path": path,
                    "priority": priority,
                    "current_url": current_url,
                    "console_errors": len(errors),
                    "console_warnings": len(warnings),
                    "api_404_count": len(api_404s),
                    "api_500_count": len(api_500s),
                    "total_api_calls": len(api_calls),
                    "status": "정상" if not errors and not api_404s and not api_500s else "문제있음"
                }
                
                results["pages"][path] = page_result
                
                # 출력
                print(f"   상태: {'✅' if page_result['status'] == '정상' else '❌'} {page_result['status']}")
                print(f"   API 호출: {len(api_calls)}개")
                
                if api_404s:
                    print(f"   🔴 404 에러: {len(api_404s)}개")
                    for err in api_404s[:2]:
                        endpoint = err["url"].split("/api/v1/")[1]
                        print(f"      - /api/v1/{endpoint}")
                    
                    # 이슈 추가
                    for err in api_404s:
                        endpoint = err["url"].split("/api/v1/")[1]
                        issue = {
                            "page": name,
                            "type": "API_404",
                            "endpoint": f"/api/v1/{endpoint}",
                            "priority": priority
                        }
                        if issue not in results["issues"]:
                            results["issues"].append(issue)
                
                if api_500s:
                    print(f"   🔴 500 에러: {len(api_500s)}개")
                
                if errors and not api_404s and not api_500s:
                    print(f"   🚨 콘솔 에러: {len(errors)}개")
                    for err in errors[:2]:
                        print(f"      - {err['text'][:80]}...")
                
            except Exception as e:
                print(f"   ❌ 페이지 로드 실패: {e}")
                results["pages"][path] = {
                    "status": "실패",
                    "error": str(e)
                }
            
            # 리스너 제거
            page.remove_listener("console", handle_console)
            page.remove_listener("request", handle_request)
            page.remove_listener("response", handle_response)
        
        await browser.close()
        
        # 3. 개발 계획 수립
        print("\n"+"="*70)
        print("🛠️ 개발 계획:")
        print("-"*70)
        
        # 이슈를 우선순위별로 정렬
        sorted_issues = sorted(results["issues"], key=lambda x: x["priority"])
        
        # 중복 제거 및 그룹화
        grouped_issues = {}
        for issue in sorted_issues:
            key = f"{issue['type']}_{issue['endpoint']}"
            if key not in grouped_issues:
                grouped_issues[key] = {
                    "type": issue["type"],
                    "endpoint": issue["endpoint"],
                    "pages": [issue["page"]],
                    "priority": issue["priority"]
                }
            else:
                if issue["page"] not in grouped_issues[key]["pages"]:
                    grouped_issues[key]["pages"].append(issue["page"])
        
        # 개발 계획 생성
        task_number = 1
        
        print("\n### 🔴 긴급 (Priority 1 - 즉시 수정 필요)")
        for key, issue in grouped_issues.items():
            if issue["priority"] == 1 and issue["type"] == "API_404":
                pages_str = ", ".join(issue["pages"])
                print(f"{task_number}. [{pages_str}] {issue['endpoint']} 엔드포인트 수정")
                
                # 가능한 원인 제시
                if issue["endpoint"].endswith("s"):
                    print(f"   → 가능한 원인: trailing slash 누락 (/{issue['endpoint']}/ 시도)")
                
                results["development_plan"].append({
                    "priority": "긴급",
                    "task": f"{issue['endpoint']} 엔드포인트 수정",
                    "affected_pages": issue["pages"],
                    "type": "API_404"
                })
                task_number += 1
        
        print("\n### ⚠️ 높음 (Priority 2 - 1주 내 수정)")
        for key, issue in grouped_issues.items():
            if issue["priority"] == 2 and issue["type"] == "API_404":
                pages_str = ", ".join(issue["pages"])
                print(f"{task_number}. [{pages_str}] {issue['endpoint']} 엔드포인트 구현")
                results["development_plan"].append({
                    "priority": "높음",
                    "task": f"{issue['endpoint']} 엔드포인트 구현",
                    "affected_pages": issue["pages"],
                    "type": "API_404"
                })
                task_number += 1
        
        # 4. 요약
        print("\n"+"="*70)
        print("📊 전체 요약:")
        
        total_pages = len(PAGES)
        healthy_pages = sum(1 for p in results["pages"].values() if p.get("status") == "정상")
        problematic_pages = total_pages - healthy_pages
        
        print(f"   총 페이지: {total_pages}개")
        print(f"   정상: {healthy_pages}개")
        print(f"   문제: {problematic_pages}개")
        print(f"   발견된 이슈: {len(results['issues'])}개")
        
        # 결과 저장
        report_file = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📁 상세 리포트: {report_file}")
        
        return results

if __name__ == "__main__":
    asyncio.run(comprehensive_check())