"""
유입고객 및 캠페인 관리 모델
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class LeadConsultationHistory(Base):
    """유입고객 상담 이력"""
    __tablename__ = "lead_consultation_history"
    
    history_id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("marketing_leads.lead_id"))
    consultation_date = Column(DateTime, nullable=False)  # 실제 DB는 timestamp
    consultation_type = Column(String(50), nullable=False)  # 전화, 방문, 온라인 등
    result = Column(String(255))  # 실제 DB 컬럼명
    notes = Column(Text)  # 실제 DB 컬럼명
    next_action = Column(String(100))
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계
    lead = relationship("MarketingLead", back_populates="consultation_history")
    created_by_user = relationship("User", foreign_keys=[created_by])


class ReregistrationCampaign(Base):
    """재등록 캠페인"""
    __tablename__ = "reregistration_campaigns"
    
    campaign_id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String(100), nullable=False)
    campaign_type = Column(String(50))  # SMS, 이메일, 전화 등
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    target_criteria = Column(Text)  # JSON 형태로 대상 조건 저장
    message_template = Column(Text)
    target_count = Column(Integer, default=0)  # DB column name
    success_count = Column(Integer, default=0)  # DB column name
    notes = Column(Text)  # Already in DB
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.user_id"))
    
    # 관계
    created_by_user = relationship("User", foreign_keys=[created_by])
    targets = relationship("CampaignTarget", back_populates="campaign")
    
    # Properties for backward compatibility
    @property
    def total_targets(self):
        return self.target_count
    
    @property
    def total_conversions(self):
        return self.success_count


class CampaignTarget(Base):
    """캠페인 대상 고객"""
    __tablename__ = "campaign_targets"
    
    target_id = Column(Integer, primary_key=True, index=True)  # Changed from 'id' to 'target_id'
    campaign_id = Column(Integer, ForeignKey("reregistration_campaigns.campaign_id"))
    lead_id = Column(Integer, ForeignKey("marketing_leads.lead_id"))
    contact_date = Column(Date)  # Changed from sent_date
    contact_result = Column(String(200))  # Changed from response_date
    converted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계
    campaign = relationship("ReregistrationCampaign", back_populates="targets")
    lead = relationship("MarketingLead", back_populates="campaign_targets")