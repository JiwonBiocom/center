"""
체험 서비스 기록 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class ExperienceServiceBase(BaseModel):
    lead_id: int
    service_date: date
    service_types: str  # "레드+림프+펄스" 형태
    before_weight: Optional[Decimal] = None
    after_weight: Optional[Decimal] = None
    before_muscle_mass: Optional[Decimal] = None
    after_muscle_mass: Optional[Decimal] = None
    before_body_fat: Optional[Decimal] = None
    after_body_fat: Optional[Decimal] = None
    phase_angle_change: Optional[Decimal] = None
    result_summary: Optional[str] = None
    staff_name: Optional[str] = Field(None, max_length=50)

class ExperienceServiceCreate(ExperienceServiceBase):
    pass

class ExperienceServiceUpdate(BaseModel):
    service_date: Optional[date] = None
    service_types: Optional[str] = None
    before_weight: Optional[Decimal] = None
    after_weight: Optional[Decimal] = None
    before_muscle_mass: Optional[Decimal] = None
    after_muscle_mass: Optional[Decimal] = None
    before_body_fat: Optional[Decimal] = None
    after_body_fat: Optional[Decimal] = None
    phase_angle_change: Optional[Decimal] = None
    result_summary: Optional[str] = None
    staff_name: Optional[str] = Field(None, max_length=50)

class ExperienceService(ExperienceServiceBase):
    experience_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True