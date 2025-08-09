"""
Smoke Tests for API Endpoints
빠른 API 동작 확인을 위한 기본 테스트
"""
import pytest
import requests
import os

API_URL = os.getenv('API_URL', 'https://aibio-api.railway.app')

class TestAPISmoke:
    """API 기본 동작 테스트"""
    
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트"""
        response = requests.get(f"{API_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    def test_login_endpoint_exists(self):
        """로그인 엔드포인트 존재 확인"""
        response = requests.post(
            f"{API_URL}/api/v1/auth/login",
            json={"username": "test", "password": "test"},
            timeout=5
        )
        # 401이어도 엔드포인트는 존재함
        assert response.status_code in [200, 401, 422]
    
    def test_customers_endpoint_requires_auth(self):
        """고객 목록 엔드포인트 인증 확인"""
        response = requests.get(f"{API_URL}/api/v1/customers/", timeout=5)
        # 401 Unauthorized 예상
        assert response.status_code == 401
    
    def test_reservations_endpoint_requires_auth(self):
        """예약 목록 엔드포인트 인증 확인"""
        response = requests.get(f"{API_URL}/api/v1/reservations/", timeout=5)
        # 401 Unauthorized 예상
        assert response.status_code == 401
    
    def test_dashboard_stats_requires_auth(self):
        """대시보드 통계 엔드포인트 인증 확인"""
        response = requests.get(f"{API_URL}/api/v1/dashboard/stats", timeout=5)
        # 401 Unauthorized 예상
        assert response.status_code == 401
    
    def test_notifications_endpoint_exists(self):
        """알림 엔드포인트 존재 확인 (trailing slash 없이)"""
        response = requests.get(f"{API_URL}/api/v1/notifications", timeout=5)
        # 401 Unauthorized 예상 (404가 아님)
        assert response.status_code == 401
    
    def test_api_response_time(self):
        """API 응답 시간 확인"""
        import time
        start = time.time()
        response = requests.get(f"{API_URL}/health", timeout=5)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0  # 2초 이내 응답