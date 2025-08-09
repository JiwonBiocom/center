from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InBodyRecordBase(BaseModel):
    measurement_date: datetime
    weight: Optional[float] = Field(None, description="체중 (kg)")
    body_fat_percentage: Optional[float] = Field(None, description="체지방률 (%)")
    skeletal_muscle_mass: Optional[float] = Field(None, description="골격근량 (kg)")
    extracellular_water_ratio: Optional[float] = Field(None, description="세포외수분비")
    phase_angle: Optional[float] = Field(None, description="위상각")
    visceral_fat_level: Optional[int] = Field(None, description="내장지방 레벨")
    notes: Optional[str] = Field(None, description="측정 관련 메모")
    measured_by: Optional[str] = Field(None, description="측정자")

class InBodyRecordCreate(InBodyRecordBase):
    customer_id: int

class InBodyRecordUpdate(BaseModel):
    measurement_date: Optional[datetime] = None
    weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    skeletal_muscle_mass: Optional[float] = None
    extracellular_water_ratio: Optional[float] = None
    phase_angle: Optional[float] = None
    visceral_fat_level: Optional[int] = None
    notes: Optional[str] = None
    measured_by: Optional[str] = None

class InBodyRecord(InBodyRecordBase):
    record_id: int
    customer_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class InBodyRecordSummary(BaseModel):
    """인바디 기록 요약 정보"""
    total_records: int
    latest_record: Optional[InBodyRecord] = None
    weight_trend: Optional[str] = None  # "increasing", "decreasing", "stable"
    body_fat_trend: Optional[str] = None
    
    class Config:
        from_attributes = True