from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class CustomerBase(BaseModel):
    # 기존 필드
    name: str = Field(..., max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    first_visit_date: Optional[date] = None
    region: Optional[str] = Field(None, max_length=100)
    referral_source: Optional[str] = Field(None, max_length=50)
    health_concerns: Optional[str] = None
    notes: Optional[str] = None
    assigned_staff: Optional[str] = Field(None, max_length=50)
    
    # 확장 필드 - 개인 정보
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=50)
    
    # 확장 필드 - 고객 상태
    membership_level: Optional[str] = Field('basic', pattern="^(basic|silver|gold|platinum|vip)$")
    customer_status: Optional[str] = Field('active', pattern="^(active|inactive|dormant)$")
    preferred_time_slots: Optional[List[str]] = None
    health_goals: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('-', '').isdigit():
            raise ValueError('전화번호는 숫자와 하이픈만 포함해야 합니다')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('올바른 이메일 형식이 아닙니다')
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    # 기존 필드
    name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    first_visit_date: Optional[date] = None
    region: Optional[str] = Field(None, max_length=100)
    referral_source: Optional[str] = Field(None, max_length=50)
    health_concerns: Optional[str] = None
    notes: Optional[str] = None
    assigned_staff: Optional[str] = Field(None, max_length=50)
    
    # 확장 필드
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=50)
    membership_level: Optional[str] = Field(None, pattern="^(basic|silver|gold|platinum|vip)$")
    customer_status: Optional[str] = Field(None, pattern="^(active|inactive|dormant)$")
    preferred_time_slots: Optional[List[str]] = None
    health_goals: Optional[str] = None

class Customer(CustomerBase):
    customer_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 통계 정보 (읽기 전용)
    last_visit_date: Optional[date] = None
    total_visits: Optional[int] = 0
    average_visit_interval: Optional[int] = None
    total_revenue: Optional[Decimal] = Decimal('0.00')
    average_satisfaction: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

# 확장된 고객 상세 정보용 스키마
class CustomerDetail(Customer):
    """고객 상세 정보 조회용 확장 스키마"""
    # 서비스 이용 요약
    service_usage_summary: Optional[dict] = None
    # 활성 패키지 정보
    active_packages: Optional[List[dict]] = None
    # 최근 서비스 이력
    recent_services: Optional[List[dict]] = None
    
    class Config:
        from_attributes = True