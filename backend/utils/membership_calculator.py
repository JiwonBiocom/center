"""
회원 등급 및 상태 자동 계산 유틸리티
"""

from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
from decimal import Decimal
import json

class MembershipCalculator:
    """회원 등급, 고객 상태, 위험 수준 자동 계산"""
    
    @staticmethod
    def calculate_membership_level(
        annual_revenue: Decimal,
        total_visits: int,
        criteria: Dict[str, Any]
    ) -> str:
        """
        연 매출과 누적 방문 횟수를 기반으로 회원 등급 계산
        
        Args:
            annual_revenue: 연간 총 매출 (원)
            total_visits: 누적 방문 횟수
            criteria: 등급 기준 설정
            
        Returns:
            회원 등급 (basic, silver, gold, platinum, vip)
        """
        revenue = float(annual_revenue)
        
        # VIP 체크 (특별 고객 - 예: 연매출 5천만원 이상)
        vip = criteria.get('vip', {})
        if revenue >= vip.get('annual_revenue_min', 50000000):
            return 'vip'
        
        # 플래티넘 체크
        platinum = criteria.get('platinum', {})
        if (revenue >= platinum.get('annual_revenue_min', 20000000) and 
            total_visits >= platinum.get('total_visits_min', 100)):
            return 'platinum'
        
        # 골드 체크
        gold = criteria.get('gold', {})
        if (revenue >= gold.get('annual_revenue_min', 10000000) and 
            total_visits >= gold.get('total_visits_min', 31) and
            total_visits <= gold.get('total_visits_max', 99)):
            return 'gold'
        
        # 실버 체크
        silver = criteria.get('silver', {})
        if (revenue >= silver.get('annual_revenue_min', 5000000) and 
            total_visits >= silver.get('total_visits_min', 11) and
            total_visits <= silver.get('total_visits_max', 30)):
            return 'silver'
        
        # 기본값은 basic
        return 'basic'
    
    @staticmethod
    def calculate_customer_status(last_visit_date: Optional[date]) -> str:
        """
        마지막 방문일을 기반으로 고객 상태 계산
        
        Args:
            last_visit_date: 마지막 방문일
            
        Returns:
            고객 상태 (active, inactive, dormant)
        """
        if not last_visit_date:
            return 'dormant'
        
        today = date.today()
        days_since_visit = (today - last_visit_date).days
        
        if days_since_visit <= 30:
            return 'active'
        elif days_since_visit <= 90:
            return 'inactive'
        else:
            return 'dormant'
    
    @staticmethod
    def calculate_risk_level(
        customer_status: str,
        visit_pattern: Dict[str, Any],
        complaint_count: int = 0
    ) -> str:
        """
        고객 상태와 방문 패턴을 기반으로 위험 수준 계산
        
        Args:
            customer_status: 현재 고객 상태
            visit_pattern: 방문 패턴 정보 (평균 방문 간격 등)
            complaint_count: 불만 접수 횟수
            
        Returns:
            위험 수준 (stable, at_risk, high_risk)
        """
        # 휴면 고객은 무조건 고위험
        if customer_status == 'dormant':
            return 'high_risk'
        
        # 불만 접수가 있으면 위험도 상승
        if complaint_count > 0:
            return 'high_risk' if complaint_count >= 2 else 'at_risk'
        
        # 비활성 고객은 위험
        if customer_status == 'inactive':
            return 'at_risk'
        
        # 방문 패턴 분석 (추후 구현 가능)
        # 예: 평균 방문 간격이 급격히 늘어난 경우 at_risk
        
        return 'stable'
    
    @staticmethod
    def calculate_annual_revenue(payments: list) -> Decimal:
        """
        최근 1년간 총 매출 계산
        
        Args:
            payments: 결제 내역 리스트
            
        Returns:
            연간 총 매출액
        """
        one_year_ago = datetime.now() - timedelta(days=365)
        annual_revenue = Decimal('0')
        
        for payment in payments:
            payment_date = payment.get('payment_date')
            if isinstance(payment_date, str):
                payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            
            if payment_date >= one_year_ago.date():
                annual_revenue += Decimal(str(payment.get('amount', 0)))
        
        return annual_revenue
    
    @staticmethod
    def get_membership_benefits(membership_level: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        회원 등급별 혜택 정보 반환
        
        Args:
            membership_level: 회원 등급
            criteria: 등급 기준 설정
            
        Returns:
            혜택 정보 딕셔너리
        """
        level_info = criteria.get(membership_level, {})
        return level_info.get('benefits', {})