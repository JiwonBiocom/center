"""
포괄적인 API 테스트 - 고객 관리 시스템 확장 기능
"""

import pytest
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
import json
import os

# 테스트 설정
BASE_URL = "http://localhost:8000"
TEST_TOKEN_FILE = "/Users/vibetj/.test_token"

class TestAPIBase:
    """API 테스트 기본 클래스"""
    
    def setup_method(self):
        """각 테스트 메소드 실행 전 인증 설정"""
        # 기존 토큰 파일이 있으면 사용
        if os.path.exists(TEST_TOKEN_FILE):
            with open(TEST_TOKEN_FILE, 'r') as f:
                token = f.read().strip()
                self.headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                return
        
        # 토큰이 없으면 로그인하여 새로 생성
        login_data = {
            "username": "admin@aibio.com",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        token_data = response.json()
        token = token_data["access_token"]
        
        # 토큰을 파일에 저장
        with open(TEST_TOKEN_FILE, 'w') as f:
            f.write(token)
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """GET 요청 헬퍼"""
        return requests.get(f"{BASE_URL}{endpoint}", headers=self.headers, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """POST 요청 헬퍼"""
        return requests.post(f"{BASE_URL}{endpoint}", headers=self.headers, json=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """PUT 요청 헬퍼"""
        return requests.put(f"{BASE_URL}{endpoint}", headers=self.headers, json=data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """DELETE 요청 헬퍼"""
        return requests.delete(f"{BASE_URL}{endpoint}", headers=self.headers)


class TestCustomersAPI(TestAPIBase):
    """고객 관리 API 테스트"""
    
    def test_customers_list(self):
        """고객 목록 조회 테스트"""
        response = self.get("/api/v1/customers/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # 데이터가 있는 경우
            customer = data[0]
            required_fields = ["customer_id", "name", "phone"]
            for field in required_fields:
                assert field in customer
    
    def test_customers_count(self):
        """고객 수 조회 테스트"""
        response = self.get("/api/v1/customers/count")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 0
    
    def test_customers_advanced_filtering(self):
        """고급 필터링 테스트"""
        # 멤버십 레벨 필터
        response = self.get("/api/v1/customers/", {
            "membership_level": "basic",
            "limit": 5
        })
        assert response.status_code == 200
        
        data = response.json()
        for customer in data:
            assert customer.get("membership_level") == "basic"
        
        # 고객 상태 필터
        response = self.get("/api/v1/customers/", {
            "customer_status": "active",
            "limit": 5
        })
        assert response.status_code == 200
        
        data = response.json()
        for customer in data:
            assert customer.get("customer_status") == "active"
    
    def test_customers_search(self):
        """고객 검색 테스트"""
        response = self.get("/api/v1/customers/", {
            "search": "김",
            "limit": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        # 검색 결과가 있다면 이름이나 전화번호에 "김"이 포함되어야 함
        for customer in data:
            name = customer.get("name", "")
            phone = customer.get("phone", "")
            assert "김" in name or "김" in phone
    
    def test_customer_detail(self):
        """고객 상세 조회 테스트"""
        # 먼저 고객 목록에서 ID 하나 가져오기
        list_response = self.get("/api/v1/customers/", {"limit": 1})
        assert list_response.status_code == 200
        
        customers = list_response.json()
        if not customers:
            pytest.skip("테스트할 고객 데이터가 없습니다")
        
        customer_id = customers[0]["customer_id"]
        
        # 고객 상세 조회
        response = self.get(f"/api/v1/customers/{customer_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["customer_id"] == customer_id


class TestCustomersExtendedAPI(TestAPIBase):
    """고객 확장 기능 API 테스트"""
    
    def test_customer_analytics(self):
        """고객 분석 데이터 조회 테스트"""
        # 고객 ID 가져오기
        list_response = self.get("/api/v1/customers/", {"limit": 1})
        assert list_response.status_code == 200
        
        customers = list_response.json()
        if not customers:
            pytest.skip("테스트할 고객 데이터가 없습니다")
        
        customer_id = customers[0]["customer_id"]
        
        # 분석 데이터 조회
        response = self.get(f"/api/v1/customers/{customer_id}/analytics")
        assert response.status_code == 200
        
        data = response.json()
        expected_keys = ["visit_summary", "service_summary", "revenue_summary", "patterns"]
        for key in expected_keys:
            assert key in data
    
    def test_customer_recommendations(self):
        """고객 추천 서비스 조회 테스트"""
        # 고객 ID 가져오기
        list_response = self.get("/api/v1/customers/", {"limit": 1})
        assert list_response.status_code == 200
        
        customers = list_response.json()
        if not customers:
            pytest.skip("테스트할 고객 데이터가 없습니다")
        
        customer_id = customers[0]["customer_id"]
        
        # 추천 서비스 조회
        response = self.get(f"/api/v1/customers/{customer_id}/recommendations")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)


class TestDashboardAPI(TestAPIBase):
    """대시보드 API 테스트"""
    
    def test_dashboard_stats(self):
        """대시보드 통계 조회 테스트"""
        response = self.get("/api/v1/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        expected_keys = ["total_customers", "total_revenue", "monthly_revenue", "active_packages"]
        for key in expected_keys:
            assert key in data
    
    def test_revenue_trend(self):
        """매출 트렌드 조회 테스트"""
        response = self.get("/api/v1/dashboard/revenue-trend")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_monthly_revenue(self):
        """월별 매출 조회 테스트"""
        response = self.get("/api/v1/dashboard/monthly-revenue")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_service_usage_stats(self):
        """서비스 사용 통계 테스트"""
        response = self.get("/api/v1/dashboard/service-usage-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestServicesAPI(TestAPIBase):
    """서비스 관리 API 테스트"""
    
    def test_service_types(self):
        """서비스 타입 조회 테스트"""
        response = self.get("/api/v1/services/types")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # 데이터가 있는 경우
            service_type = data[0]
            required_fields = ["service_type_id", "service_name"]
            for field in required_fields:
                assert field in service_type
    
    def test_service_usage(self):
        """서비스 사용 내역 조회 테스트"""
        response = self.get("/api/v1/services/usage")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_service_calendar(self):
        """서비스 캘린더 조회 테스트"""
        response = self.get("/api/v1/services/calendar")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestPaymentsAPI(TestAPIBase):
    """결제 관리 API 테스트"""
    
    def test_payments_list(self):
        """결제 목록 조회 테스트"""
        response = self.get("/api/v1/payments/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_payment_stats_summary(self):
        """결제 통계 요약 조회 테스트"""
        response = self.get("/api/v1/payments/stats/summary")
        assert response.status_code == 200
        
        data = response.json()
        expected_keys = ["total_amount", "total_count", "average_amount"]
        for key in expected_keys:
            assert key in data


class TestPackagesAPI(TestAPIBase):
    """패키지 관리 API 테스트"""
    
    def test_packages_list(self):
        """패키지 목록 조회 테스트"""
        response = self.get("/api/v1/packages/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_package_purchases_stats(self):
        """패키지 구매 통계 테스트"""
        response = self.get("/api/v1/packages/purchases/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)


class TestReservationsAPI(TestAPIBase):
    """예약 관리 API 테스트"""
    
    def test_reservations_list(self):
        """예약 목록 조회 테스트"""
        response = self.get("/api/v1/reservations/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestLeadsAPI(TestAPIBase):
    """리드 관리 API 테스트"""
    
    def test_leads_list(self):
        """리드 목록 조회 테스트"""
        response = self.get("/api/v1/leads/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestKitsAPI(TestAPIBase):
    """키트 관리 API 테스트"""
    
    def test_kits_list(self):
        """키트 목록 조회 테스트"""
        response = self.get("/api/v1/kits/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestAuthAPI(TestAPIBase):
    """인증 API 테스트"""
    
    def test_current_user(self):
        """현재 사용자 정보 조회 테스트"""
        response = self.get("/api/v1/auth/me")
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "name" in data
        assert "role" in data


class TestSettingsAPI(TestAPIBase):
    """설정 API 테스트"""
    
    def test_system_company(self):
        """회사 정보 조회 테스트"""
        response = self.get("/api/v1/settings/system/company")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
    
    def test_users_list(self):
        """사용자 목록 조회 테스트"""
        response = self.get("/api/v1/settings/users")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_notification_preferences(self):
        """알림 설정 조회 테스트"""
        response = self.get("/api/v1/settings/notifications/preferences")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)


class TestHealthCheck(TestAPIBase):
    """헬스체크 및 기본 엔드포인트 테스트"""
    
    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self):
        """헬스체크 테스트"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    # 개별 테스트 실행을 위한 메인 함수
    pytest.main([__file__, "-v"])