from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import date, datetime
from decimal import Decimal

class MarketingLeadBase(BaseModel):
    name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    lead_date: date  # 필수 필드로 변경
    age: Optional[int] = None
    region: Optional[str] = Field(None, max_length=50)
    lead_channel: Optional[str] = Field(None, max_length=50)
    carrot_id: Optional[str] = Field(None, max_length=100)
    ad_watched: Optional[str] = Field(None, max_length=100)
    price_informed: Optional[bool] = False
    ab_test_group: Optional[str] = Field(None, max_length=20)
    
    # 날짜 필드들
    db_entry_date: Optional[date] = None
    phone_consult_date: Optional[date] = None
    visit_consult_date: Optional[date] = None
    registration_date: Optional[date] = None
    
    # 추가된 필드들
    db_channel: Optional[str] = Field(None, max_length=50)
    phone_consult_result: Optional[str] = Field(None, max_length=100)
    remind_date: Optional[date] = None
    visit_cancelled: Optional[bool] = False
    visit_cancel_reason: Optional[str] = None
    
    # 재등록 관련
    is_reregistration_target: Optional[bool] = False
    last_service_date: Optional[date] = None
    reregistration_proposal_date: Optional[date] = None
    
    # 구매 정보
    purchased_product: Optional[str] = Field(None, max_length=200)
    no_registration_reason: Optional[str] = None
    notes: Optional[str] = None
    revenue: Optional[Decimal] = None
    
    # 상태 및 담당자
    status: Optional[str] = Field("new", max_length=20)
    assigned_staff_id: Optional[int] = None
    converted_customer_id: Optional[int] = None
    
    # 추가 상담 정보 필드
    consultant_name: Optional[str] = Field(None, max_length=50)
    current_weight: Optional[Decimal] = None
    target_weight: Optional[Decimal] = None
    exercise_plan: Optional[str] = None
    diet_plan: Optional[str] = None
    experience_services: Optional[str] = None
    experience_result: Optional[str] = None
    rejection_reason: Optional[str] = None
    past_diet_experience: Optional[str] = None
    main_concerns: Optional[str] = None
    referral_detail: Optional[str] = None
    visit_purpose: Optional[str] = None

class MarketingLeadCreate(MarketingLeadBase):
    pass

class MarketingLeadUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    lead_date: Optional[date] = None
    age: Optional[int] = None
    region: Optional[str] = Field(None, max_length=50)
    lead_channel: Optional[str] = Field(None, max_length=50)
    carrot_id: Optional[str] = Field(None, max_length=100)
    ad_watched: Optional[str] = Field(None, max_length=100)
    price_informed: Optional[bool] = None
    ab_test_group: Optional[str] = Field(None, max_length=20)
    
    # 날짜 필드들
    db_entry_date: Optional[date] = None
    phone_consult_date: Optional[date] = None
    visit_consult_date: Optional[date] = None
    registration_date: Optional[date] = None
    
    # 추가된 필드들
    db_channel: Optional[str] = Field(None, max_length=50)
    phone_consult_result: Optional[str] = Field(None, max_length=100)
    remind_date: Optional[date] = None
    visit_cancelled: Optional[bool] = None
    visit_cancel_reason: Optional[str] = None
    
    # 재등록 관련
    is_reregistration_target: Optional[bool] = None
    last_service_date: Optional[date] = None
    reregistration_proposal_date: Optional[date] = None
    
    # 구매 정보
    purchased_product: Optional[str] = Field(None, max_length=200)
    no_registration_reason: Optional[str] = None
    notes: Optional[str] = None
    revenue: Optional[Decimal] = None
    
    # 상태 및 담당자
    status: Optional[str] = Field(None, max_length=20)
    assigned_staff_id: Optional[int] = None
    converted_customer_id: Optional[int] = None
    
    # 추가 상담 정보 필드
    consultant_name: Optional[str] = Field(None, max_length=50)
    current_weight: Optional[Decimal] = None
    target_weight: Optional[Decimal] = None
    exercise_plan: Optional[str] = None
    diet_plan: Optional[str] = None
    experience_services: Optional[str] = None
    experience_result: Optional[str] = None
    rejection_reason: Optional[str] = None
    past_diet_experience: Optional[str] = None
    main_concerns: Optional[str] = None
    referral_detail: Optional[str] = None
    visit_purpose: Optional[str] = None

class MarketingLead(MarketingLeadBase):
    lead_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 관계 필드
    assigned_staff_name: Optional[str] = None
    converted_customer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# 상담 이력 스키마
class ConsultationHistoryBase(BaseModel):
    lead_id: int
    consultation_type: str  # phone, visit, online, follow_up
    consultation_date: datetime
    consulted_by: str
    consultation_content: str
    next_action: Optional[str] = None
    next_action_date: Optional[date] = None
    result: Optional[str] = None
    
    # 추가 필드
    visit_purpose: Optional[str] = None
    main_needs: Optional[str] = None
    current_condition: Optional[str] = None
    estimated_revenue: Optional[Decimal] = None

class ConsultationHistoryCreate(ConsultationHistoryBase):
    pass

class ConsultationHistoryUpdate(BaseModel):
    consultation_date: Optional[datetime] = None
    consultation_type: Optional[str] = None
    consulted_by: Optional[str] = None
    consultation_content: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[date] = None
    result: Optional[str] = None

class ConsultationHistory(ConsultationHistoryBase):
    consultation_id: int
    created_by: Optional[int] = None
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 재등록 캠페인 스키마
class CampaignBase(BaseModel):
    campaign_name: str = Field(..., max_length=100)
    start_date: date
    end_date: Optional[date] = None
    target_criteria: Optional[dict] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = True

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    campaign_name: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_criteria: Optional[dict] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class Campaign(CampaignBase):
    campaign_id: int
    target_count: int = 0
    success_count: int = 0
    created_by: Optional[int] = None
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 캠페인 대상 스키마
class CampaignTargetBase(BaseModel):
    campaign_id: int
    lead_id: int
    contact_date: Optional[date] = None
    contact_result: Optional[str] = Field(None, max_length=100)
    converted: Optional[bool] = False

class CampaignTargetCreate(CampaignTargetBase):
    pass

class CampaignTarget(CampaignTargetBase):
    target_id: int
    created_at: datetime
    lead_name: Optional[str] = None
    lead_phone: Optional[str] = None
    
    class Config:
        from_attributes = True


# 필터 스키마
class MarketingLeadFilter(BaseModel):
    # 기간 필터
    db_entry_date_from: Optional[date] = None
    db_entry_date_to: Optional[date] = None
    lead_date_from: Optional[date] = None
    lead_date_to: Optional[date] = None
    
    # 상태 필터
    status: Optional[List[str]] = None
    has_phone_consult: Optional[bool] = None
    has_visit_consult: Optional[bool] = None
    is_registered: Optional[bool] = None
    is_reregistration_target: Optional[bool] = None
    
    # 채널 필터
    lead_channel: Optional[List[str]] = None
    db_channel: Optional[List[str]] = None
    
    # 기타 필터
    age_from: Optional[int] = None
    age_to: Optional[int] = None
    region: Optional[List[str]] = None
    assigned_staff_id: Optional[int] = None
    
    # 검색
    search: Optional[str] = None  # 이름, 전화번호, 비고