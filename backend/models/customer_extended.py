"""
고객 관련 확장 모델들
- CustomerPreference: 고객 선호도
- CustomerAnalytics: 고객 분석 데이터
- MarketingLead: 마케팅 리드
- KitReceipt: 키트 수령 정보
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class CustomerPreference(Base):
    """고객 선호도 정보"""
    __tablename__ = "customer_preferences"
    
    preference_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), unique=True)
    preferred_services = Column(ARRAY(Text))  # ['brain', 'pulse', 'lymph', 'red', 'ai_bike']
    preferred_time = Column(String(20))  # morning, afternoon, evening
    preferred_intensity = Column(String(20))  # low, medium, high
    health_interests = Column(ARRAY(Text))  # ['stress_relief', 'sleep_quality', 'weight_loss']
    communication_preference = Column(String(20))  # kakao, sms, email
    marketing_consent = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="preferences")


class CustomerAnalytics(Base):
    """고객 분석 데이터"""
    __tablename__ = "customer_analytics"
    
    analytics_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"))
    analysis_date = Column(Date, nullable=False)
    visit_frequency = Column(String(20))  # daily, weekly, bi-weekly, monthly
    consistency_score = Column(Integer)  # 0-100
    most_used_service = Column(String(20))
    ltv_estimate = Column(DECIMAL(10, 2))  # Lifetime Value 추정치
    churn_risk = Column(String(20))  # low, medium, high
    churn_probability = Column(Integer)  # 0-100
    retention_score = Column(Integer)  # 0-100
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="analytics")


class MarketingLead(Base):
    """마케팅 리드 (유입 고객)"""
    __tablename__ = "marketing_leads"
    
    lead_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), index=True)
    lead_date = Column(Date, nullable=False)  # 리드 발생일
    age = Column(Integer)
    region = Column(String(50))
    lead_channel = Column(String(50), index=True)  # youtube, carrot, meta, friend, search
    carrot_id = Column(String(100))  # 당근마켓 아이디
    ad_watched = Column(String(100))  # 시청한 광고
    price_informed = Column(Boolean, default=False)
    ab_test_group = Column(String(20))
    
    # 기본 날짜 정보
    db_entry_date = Column(Date)
    phone_consult_date = Column(Date)
    visit_consult_date = Column(Date)
    registration_date = Column(Date)
    
    # 추가된 필드들
    db_channel = Column(String(50), index=True)  # 홈페이지, 당근, 플레이스, 전화, 방문 등
    phone_consult_result = Column(String(100))  # 전화상담 결과
    remind_date = Column(Date)  # 리마인드 날짜
    visit_cancelled = Column(Boolean, default=False)  # 방문 취소 여부
    visit_cancel_reason = Column(Text)  # 방문 취소 사유
    
    # 재등록 관련
    is_reregistration_target = Column(Boolean, default=False, index=True)
    last_service_date = Column(Date)
    reregistration_proposal_date = Column(Date)
    
    # 구매 정보
    purchased_product = Column(String(200))
    no_registration_reason = Column(Text)
    notes = Column(Text)
    revenue = Column(DECIMAL(10, 2))
    
    # 상태 및 담당자
    status = Column(String(20), default='new', index=True)  # new, contacted, consulted, converted, lost
    assigned_staff_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    converted_customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    
    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    converted_customer = relationship("Customer", back_populates="lead_source")
    assigned_staff = relationship("User", backref="assigned_leads")
    consultation_history = relationship("LeadConsultationHistory", back_populates="lead", order_by="desc(LeadConsultationHistory.consultation_date)")
    campaign_targets = relationship("CampaignTarget", back_populates="lead")


class KitReceipt(Base):
    """키트 수령 정보"""
    __tablename__ = "kit_receipts"
    
    kit_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"))
    kit_type = Column(String(100))  # 키트 종류
    serial_number = Column(String(100), unique=True, index=True)
    receipt_date = Column(Date)  # 키트 수령일
    result_received_date = Column(Date)  # 결과지 수령일
    result_delivered_date = Column(Date)  # 결과지 전달일
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="kit_receipts")