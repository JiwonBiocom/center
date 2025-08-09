#!/usr/bin/env python3
"""
전체 기능 테스트 스크립트
각 주요 기능의 API 엔드포인트를 확인하여 404나 500 에러가 있는지 검사합니다.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, date
from typing import Dict, List, Tuple

# API 기본 URL
API_URL = "https://center-production-1421.up.railway.app"

# 테스트할 엔드포인트 목록
ENDPOINTS_TO_TEST = [
    # Dashboard
    ("GET", "/api/v1/dashboard/stats", None, "대시보드 통계"),
    ("GET", "/api/v1/dashboard/revenue-trend", None, "매출 트렌드"),
    ("GET", "/api/v1/dashboard/monthly-revenue", None, "월별 매출"),
    ("GET", "/api/v1/dashboard/service-usage-stats", None, "서비스 사용 현황"),

    # Customers
    ("GET", "/api/v1/customers", None, "고객 목록"),
    ("GET", "/api/v1/customers/count", None, "고객 수"),
    ("GET", "/api/v1/customers/1", None, "고객 상세 (ID=1)"),

    # Services
    ("GET", "/api/v1/services/usage", None, "서비스 이용 내역"),
    ("GET", "/api/v1/services/calendar", {"year": 2025, "month": 3}, "서비스 캘린더"),

    # Payments
    ("GET", "/api/v1/payments/", None, "결제 목록"),
    ("GET", "/api/v1/payments/stats/summary", None, "결제 통계"),

    # Reports
    ("GET", "/api/v1/reports/summary", None, "보고서 요약"),
    ("GET", "/api/v1/reports/revenue/monthly", None, "월별 매출 보고서"),
    ("GET", "/api/v1/reports/customers/acquisition", None, "고객 획득 보고서"),
    ("GET", "/api/v1/reports/services/usage", None, "서비스 사용 보고서"),
    ("GET", "/api/v1/reports/staff/performance", None, "직원 성과 보고서"),

    # PDF Generation
    ("GET", f"/api/v1/reports/revenue/generate/monthly-revenue?year=2025&month=3", None, "월간 매출 PDF"),
    ("GET", f"/api/v1/reports/customers/generate/customer-analysis?start_date=2025-01-01&end_date=2025-03-31", None, "고객 분석 PDF"),

    # Reservations
    ("GET", "/api/v1/reservations/", None, "예약 목록"),
    ("GET", "/api/v1/reservations/slots/available", {"date": "2025-03-01", "service_type_id": 1}, "예약 가능 시간"),

    # Notifications
    ("GET", "/api/v1/notifications", None, "알림 목록"),
    ("GET", "/api/v1/notifications/stats", None, "알림 통계"),

    # Settings
    ("GET", "/api/v1/settings/system/company", None, "회사 정보"),
    ("GET", "/api/v1/settings/notifications/preferences", None, "알림 설정"),
    ("GET", "/api/v1/settings/users", None, "사용자 목록"),

    # Master (권한 필요)
    ("GET", "/api/v1/master/users", None, "마스터 - 사용자 목록"),
    ("GET", "/api/v1/master/system/overview", None, "마스터 - 시스템 개요"),
]

class APITester:
    def __init__(self, token: str = None):
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def test_endpoint(self, session: aiohttp.ClientSession, method: str, path: str, params: Dict = None, name: str = "") -> Tuple[str, int, str]:
        """단일 엔드포인트 테스트"""
        url = f"{API_URL}{path}"

        try:
            async with session.request(method, url, headers=self.headers, params=params, ssl=False) as response:
                status = response.status

                # 응답 본문 읽기
                try:
                    data = await response.json()
                    error_msg = data.get("error", {}).get("message", "") if "error" in data else ""
                except:
                    error_msg = await response.text()

                return name or path, status, error_msg

        except Exception as e:
            return name or path, -1, str(e)

    async def run_tests(self) -> List[Tuple[str, int, str]]:
        """모든 엔드포인트 테스트 실행"""
        results = []

        async with aiohttp.ClientSession() as session:
            # 먼저 로그인 시도
            if not self.token:
                print("🔐 로그인 중...")
                login_data = {"email": "admin@aibio.kr", "password": "admin123"}

                try:
                    async with session.post(f"{API_URL}/api/v1/auth/login", json=login_data, ssl=False) as response:
                        if response.status == 200:
                            data = await response.json()
                            # API 응답 형식 확인
                            if "access_token" in data:
                                self.token = data["access_token"]
                            elif "data" in data and "access_token" in data.get("data", {}):
                                self.token = data["data"]["access_token"]
                            else:
                                print(f"⚠️  토큰을 찾을 수 없음: {data}")

                            if self.token:
                                self.headers["Authorization"] = f"Bearer {self.token}"
                                print("✅ 로그인 성공")
                            else:
                                print("❌ 로그인은 성공했으나 토큰이 없음")
                        else:
                            print("❌ 로그인 실패")
                except Exception as e:
                    print(f"❌ 로그인 에러: {e}")

            # 엔드포인트 테스트
            print("\n🧪 API 엔드포인트 테스트 시작...\n")

            for method, path, params, name in ENDPOINTS_TO_TEST:
                result = await self.test_endpoint(session, method, path, params, name)
                results.append(result)

                # 결과 출력
                emoji = "✅" if result[1] == 200 else "❌"
                print(f"{emoji} {result[0]}: {result[1]}", end="")
                if result[1] not in [200, 404]:  # 404는 예상 가능한 에러
                    print(f" - {result[2]}", end="")
                print()

        return results

def main():
    """메인 함수"""
    print("=" * 60)
    print("AIBIO 센터 관리 시스템 - 전체 기능 테스트")
    print("=" * 60)

    tester = APITester()
    results = asyncio.run(tester.run_tests())

    # 통계 출력
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    total = len(results)
    success = len([r for r in results if r[1] == 200])
    not_found = len([r for r in results if r[1] == 404])
    errors = len([r for r in results if r[1] not in [200, 404]])

    print(f"✅ 성공: {success}/{total}")
    print(f"⚠️  404 Not Found: {not_found}")
    print(f"❌ 기타 에러: {errors}")

    # 에러 상세
    if errors > 0:
        print("\n🚨 에러 상세:")
        for name, status, error in results:
            if status not in [200, 404]:
                print(f"  - {name}: {status} - {error}")

    # 404 상세
    if not_found > 0:
        print("\n⚠️  구현되지 않은 엔드포인트:")
        for name, status, error in results:
            if status == 404:
                print(f"  - {name}")

if __name__ == "__main__":
    main()
