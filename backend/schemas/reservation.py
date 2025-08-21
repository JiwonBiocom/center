from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import date, time, datetime
from models.reservation import ReservationStatus

class ReservationBase(BaseModel):
    customer_id: int
    service_type_id: int
    staff_id: Optional[int] = None
    reservation_date: date
    reservation_time: time
    duration_minutes: int = 60
    customer_request: Optional[str] = None
    internal_memo: Optional[str] = None

class ReservationCreate(BaseModel):
    customer_id: Optional[int] = None  # Make optional for guest customers
    customer_name: Optional[str] = None  # For unregistered customers
    customer_phone: Optional[str] = None  # For unregistered customers
    service_type_id: int
    staff_id: Optional[int] = None
    reservation_date: date
    reservation_time: time
    duration_minutes: int = 60
    customer_request: Optional[str] = None
    internal_memo: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_customer(self):
        if not self.customer_id and not self.customer_name:
            raise ValueError('Either customer_id or customer_name must be provided')
        return self

class ReservationUpdate(BaseModel):
    service_type_id: Optional[int] = None
    staff_id: Optional[int] = None
    reservation_date: Optional[date] = None
    reservation_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    status: Optional[ReservationStatus] = None
    customer_request: Optional[str] = None
    internal_memo: Optional[str] = None

class ReservationCancel(BaseModel):
    cancel_reason: str

class ReservationResponse(BaseModel):
    reservation_id: int
    customer_id: int  # This will always have a value after creation
    service_type_id: int
    staff_id: Optional[int] = None
    reservation_date: date
    reservation_time: time
    duration_minutes: int
    status: ReservationStatus
    customer_request: Optional[str] = None
    internal_memo: Optional[str] = None
    reminder_sent: bool
    confirmation_sent: bool
    created_at: datetime
    updated_at: datetime
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None

    # 관계 데이터
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    service_name: Optional[str] = None
    staff_name: Optional[str] = None

    class Config:
        from_attributes = True

class ReservationSlotBase(BaseModel):
    staff_id: int
    day_of_week: Optional[int] = Field(None, ge=0, le=6)  # 0=월, 6=일
    start_time: time
    end_time: time
    is_available: bool = True
    specific_date: Optional[date] = None

class ReservationSlotCreate(ReservationSlotBase):
    pass

class ReservationSlotResponse(ReservationSlotBase):
    slot_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AvailableSlot(BaseModel):
    date: date
    time: time
    staff_id: Optional[int] = None
    staff_name: Optional[str] = None

class KakaoTemplateBase(BaseModel):
    template_code: str
    template_name: str
    template_type: str
    content: str
    variables: Optional[List[str]] = None

class KakaoTemplateCreate(KakaoTemplateBase):
    pass

class KakaoTemplateResponse(KakaoTemplateBase):
    template_id: int
    is_active: bool
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class KakaoMessageRequest(BaseModel):
    reservation_id: int
    template_type: str  # confirmation, reminder, change, cancel

class KakaoMessageLogResponse(BaseModel):
    log_id: int
    reservation_id: Optional[int] = None
    customer_id: int
    phone_number: str
    message_type: str
    status: str
    content: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
