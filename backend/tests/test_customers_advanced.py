"""
고객 관리 고급 기능 전용 테스트
"""

import pytest
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
import os

BASE_URL = "http://localhost:8000"
TEST_TOKEN_FILE = "/Users/vibetj/.test_token"

class TestCustomersAdvanced:
    """고객 관리 고급 기능 테스트"""
    
    def setup_method(self):
        """각 테스트 메소드 실행 전 인증 설정"""
        if os.path.exists(TEST_TOKEN_FILE):
            with open(TEST_TOKEN_FILE, 'r') as f:
                token = f.read().strip()
        else:
            # 로그인하여 토큰 생성
            login_data = {
                "username": "admin@aibio.com", 
                "password": "admin123"
            }
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200
            token = response.json()["access_token"]
            with open(TEST_TOKEN_FILE, 'w') as f:
                f.write(token)
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_customers(self, params: Dict = None) -> List[Dict]:
        """고객 목록 조회 헬퍼"""
        response = requests.get(
            f"{BASE_URL}/api/v1/customers/",
            headers=self.headers,
            params=params or {}
        )
        assert response.status_code == 200
        return response.json()
    
    def get_customer_count(self, params: Dict = None) -> int:
        """고객 수 조회 헬퍼"""
        response = requests.get(
            f"{BASE_URL}/api/v1/customers/count",
            headers=self.headers,
            params=params or {}
        )
        assert response.status_code == 200
        return response.json()["count"]
    
    def test_membership_level_filtering(self):
        """멤버십 레벨별 필터링 테스트"""
        levels = ["basic", "premium", "vip"]
        
        for level in levels:
            customers = self.get_customers({"membership_level": level, "limit": 10})
            for customer in customers:
                assert customer.get("membership_level") == level, f"고객 {customer.get('name')}의 멤버십 레벨이 {level}이 아닙니다"
    
    def test_customer_status_filtering(self):
        """고객 상태별 필터링 테스트"""
        statuses = ["active", "inactive", "dormant"]
        
        for status in statuses:
            customers = self.get_customers({"customer_status": status, "limit": 10})
            for customer in customers:
                assert customer.get("customer_status") == status, f"고객 {customer.get('name')}의 상태가 {status}가 아닙니다"
    
    def test_risk_level_filtering(self):
        """위험도별 필터링 테스트"""
        risk_levels = ["stable", "warning", "danger"]
        
        for risk_level in risk_levels:
            customers = self.get_customers({"risk_level": risk_level, "limit": 10})
            for customer in customers:
                assert customer.get("risk_level") == risk_level, f"고객 {customer.get('name')}의 위험도가 {risk_level}이 아닙니다"
    
    def test_region_filtering(self):
        """지역별 필터링 테스트"""
        regions = ["서울", "인천", "경기"]
        
        for region in regions:
            customers = self.get_customers({"region": region, "limit": 10})
            for customer in customers:
                customer_region = customer.get("region", "")
                assert region in customer_region, f"고객 {customer.get('name')}의 지역 '{customer_region}'에 '{region}'이 포함되지 않았습니다"
    
    def test_referral_source_filtering(self):
        """유입 경로별 필터링 테스트"""
        sources = ["당근", "바이오컴", "온라인", "추천"]
        
        for source in sources:
            customers = self.get_customers({"referral_source": source, "limit": 10})
            for customer in customers:
                assert customer.get("referral_source") == source, f"고객 {customer.get('name')}의 유입경로가 {source}가 아닙니다"
    
    def test_age_range_filtering(self):
        """나이 범위 필터링 테스트"""
        current_year = datetime.now().year
        
        # 20-30세 필터링
        customers = self.get_customers({
            "age_min": 20,
            "age_max": 30,
            "limit": 10
        })
        
        for customer in customers:
            birth_year = customer.get("birth_year")
            if birth_year:  # birth_year가 있는 경우만 검증
                age = current_year - birth_year
                assert 20 <= age <= 30, f"고객 {customer.get('name')}의 나이 {age}가 20-30 범위를 벗어났습니다"
    
    def test_revenue_range_filtering(self):
        """매출 범위 필터링 테스트"""
        # 10만원 이상 고객 필터링
        customers = self.get_customers({
            "revenue_min": 10,  # 10만원
            "limit": 10
        })
        
        for customer in customers:
            revenue = float(customer.get("total_revenue", 0))
            assert revenue >= 100000, f"고객 {customer.get('name')}의 총 매출 {revenue}이 10만원 미만입니다"
    
    def test_visits_range_filtering(self):
        """방문 횟수 범위 필터링 테스트"""
        # 5회 이상 방문한 고객 필터링
        customers = self.get_customers({
            "visits_min": 5,
            "limit": 10
        })
        
        for customer in customers:
            visits = customer.get("total_visits", 0)
            assert visits >= 5, f"고객 {customer.get('name')}의 총 방문횟수 {visits}이 5회 미만입니다"
    
    def test_date_range_filtering(self):
        """날짜 범위 필터링 테스트"""
        # 2025년 5월에 첫 방문한 고객 필터링
        customers = self.get_customers({
            "first_visit_from": "2025-05-01",
            "first_visit_to": "2025-05-31",
            "limit": 10
        })
        
        for customer in customers:
            first_visit = customer.get("first_visit_date")
            if first_visit:
                visit_date = datetime.strptime(first_visit, "%Y-%m-%d").date()
                assert date(2025, 5, 1) <= visit_date <= date(2025, 5, 31), \
                    f"고객 {customer.get('name')}의 첫 방문일 {first_visit}이 2025년 5월 범위를 벗어났습니다"
    
    def test_combined_filtering(self):
        """복합 필터링 테스트"""
        # 여러 필터 조건을 동시에 적용
        customers = self.get_customers({
            "membership_level": "basic",
            "customer_status": "active",
            "region": "서울",
            "limit": 5
        })
        
        for customer in customers:
            assert customer.get("membership_level") == "basic"
            assert customer.get("customer_status") == "active"
            assert "서울" in customer.get("region", "")
    
    def test_search_with_filters(self):
        """검색과 필터 조합 테스트"""
        customers = self.get_customers({
            "search": "김",
            "membership_level": "basic",
            "limit": 5
        })
        
        for customer in customers:
            # 검색 조건 확인
            name = customer.get("name", "")
            phone = customer.get("phone", "")
            email = customer.get("email", "")
            assert "김" in name or "김" in phone or "김" in email
            
            # 필터 조건 확인
            assert customer.get("membership_level") == "basic"
    
    def test_pagination_with_filters(self):
        """필터링된 결과의 페이지네이션 테스트"""
        # 첫 번째 페이지
        page1 = self.get_customers({
            "membership_level": "basic",
            "skip": 0,
            "limit": 5
        })
        
        # 두 번째 페이지
        page2 = self.get_customers({
            "membership_level": "basic",
            "skip": 5,
            "limit": 5
        })
        
        # 페이지가 겹치지 않는지 확인
        page1_ids = {c["customer_id"] for c in page1}
        page2_ids = {c["customer_id"] for c in page2}
        
        assert page1_ids.isdisjoint(page2_ids), "페이지네이션 결과가 겹칩니다"
    
    def test_count_consistency(self):
        """목록 조회와 카운트 조회의 일관성 테스트"""
        filter_params = {
            "membership_level": "basic",
            "customer_status": "active"
        }
        
        # 전체 목록 조회 (큰 limit)
        all_customers = self.get_customers({**filter_params, "limit": 1000})
        
        # 카운트 조회
        count = self.get_customer_count(filter_params)
        
        assert len(all_customers) == count, f"목록 조회 결과 {len(all_customers)}개와 카운트 조회 결과 {count}개가 일치하지 않습니다"
    
    def test_empty_filter_results(self):
        """빈 결과를 반환하는 필터 테스트"""
        # 존재하지 않는 조건으로 필터링
        customers = self.get_customers({
            "membership_level": "nonexistent",
            "limit": 10
        })
        
        assert len(customers) == 0, "존재하지 않는 멤버십 레벨로 필터링했는데 결과가 반환되었습니다"
        
        count = self.get_customer_count({"membership_level": "nonexistent"})
        assert count == 0, "존재하지 않는 멤버십 레벨의 카운트가 0이 아닙니다"
    
    def test_filter_parameter_validation(self):
        """필터 매개변수 유효성 검사 테스트"""
        # 잘못된 날짜 형식
        response = requests.get(
            f"{BASE_URL}/api/v1/customers/",
            headers=self.headers,
            params={"first_visit_from": "invalid-date"}
        )
        # 400 Bad Request 또는 422 Unprocessable Entity 예상
        assert response.status_code in [400, 422]
        
        # 음수 나이
        response = requests.get(
            f"{BASE_URL}/api/v1/customers/",
            headers=self.headers,
            params={"age_min": -5}
        )
        # 잘못된 값이지만 서버에서 처리할 수 있음 (필터 결과가 없을 뿐)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])