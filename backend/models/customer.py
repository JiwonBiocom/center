from sqlalchemy import Column, Integer, String, Date, DateTime, Text, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from typing import Dict, Any, Optional
from datetime import date
from decimal import Decimal

class Customer(Base):
    __tablename__ = "customers"
    
    # 기존 컬럼
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), unique=True, index=True)
    first_visit_date = Column(Date)
    region = Column(String(100))
    referral_source = Column(String(50))
    health_concerns = Column(Text)
    notes = Column(Text)
    assigned_staff = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 확장 컬럼 - 개인 정보
    birth_year = Column(Integer)
    gender = Column(String(10))
    email = Column(String(100))
    address = Column(Text)
    emergency_contact = Column(String(100))
    occupation = Column(String(50))
    
    # 확장 컬럼 - 고객 상태
    membership_level = Column(String(20), default='basic')  # basic, premium, vip
    customer_status = Column(String(20), default='active')  # active, inactive, dormant
    preferred_time_slots = Column(JSONB)  # ["morning", "afternoon", "evening", "weekend"]
    health_goals = Column(Text)
    
    # 확장 컬럼 - 통계 정보
    last_visit_date = Column(Date)
    total_visits = Column(Integer, default=0)
    average_visit_interval = Column(Integer)  # 평균 방문 주기 (일)
    total_revenue = Column(DECIMAL(10, 2), default=0)
    average_satisfaction = Column(DECIMAL(3, 2))  # 1.00 ~ 5.00
    
    # Enhanced service relationships (commented out - models not yet implemented)
    # service_sessions = relationship("ServiceSession", back_populates="customer")
    # enhanced_package_usages = relationship("EnhancedPackageUsage", back_populates="customer")
    # service_preferences = relationship("CustomerServicePreference", back_populates="customer")
    
    # Extended relationships
    preferences = relationship("CustomerPreference", back_populates="customer", uselist=False)
    analytics = relationship("CustomerAnalytics", back_populates="customer")
    kit_receipts = relationship("KitReceipt", back_populates="customer")
    lead_source = relationship("MarketingLead", back_populates="converted_customer", uselist=False)
    inbody_records = relationship("InBodyRecord", back_populates="customer")
    
    def update_membership_level(self, criteria: Dict[str, Any], annual_revenue: Optional[Decimal] = None) -> str:
        """
        회원 등급 자동 계산 및 업데이트
        
        Args:
            criteria: 등급 기준 설정
            annual_revenue: 연간 매출 (제공되지 않으면 total_revenue 사용)
            
        Returns:
            계산된 회원 등급
        """
        revenue = float(annual_revenue or self.total_revenue or 0)
        visits = self.total_visits or 0
        
        # VIP 체크 (특별 고객 - 예: 연매출 5천만원 이상)
        vip = criteria.get('vip', {})
        if revenue >= vip.get('annual_revenue_min', 50000000):
            self.membership_level = 'vip'
            return 'vip'
        
        # 플래티넘 체크
        platinum = criteria.get('platinum', {})
        if (revenue >= platinum.get('annual_revenue_min', 20000000) and 
            visits >= platinum.get('total_visits_min', 100)):
            self.membership_level = 'platinum'
            return 'platinum'
        
        # 골드 체크
        gold = criteria.get('gold', {})
        if (revenue >= gold.get('annual_revenue_min', 10000000) and 
            visits >= gold.get('total_visits_min', 31) and
            visits <= gold.get('total_visits_max', 99)):
            self.membership_level = 'gold'
            return 'gold'
        
        # 실버 체크
        silver = criteria.get('silver', {})
        if (revenue >= silver.get('annual_revenue_min', 5000000) and 
            visits >= silver.get('total_visits_min', 11) and
            visits <= silver.get('total_visits_max', 30)):
            self.membership_level = 'silver'
            return 'silver'
        
        # 기본값은 basic
        self.membership_level = 'basic'
        return 'basic'
    
    def update_customer_status(self) -> str:
        """
        마지막 방문일 기반 고객 상태 자동 업데이트
        - Active: 30일 이내 방문
        - Inactive: 31-90일 사이 방문
        - Dormant: 90일 초과 미방문
        
        Returns:
            계산된 고객 상태
        """
        if not self.last_visit_date:
            self.customer_status = 'dormant'
            return 'dormant'
        
        today = date.today()
        days_since_visit = (today - self.last_visit_date).days
        
        if days_since_visit <= 30:
            self.customer_status = 'active'
        elif days_since_visit <= 90:
            self.customer_status = 'inactive'
        else:
            self.customer_status = 'dormant'
        
        return self.customer_status
    
