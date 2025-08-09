from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import date, datetime
from decimal import Decimal

class PaymentBase(BaseModel):
    customer_id: int
    payment_date: date
    amount: Decimal = Field(..., decimal_places=2, gt=0)
    payment_method: Literal['card', 'transfer', 'cash', 'other']
    payment_type: Optional[Literal['package', 'single', 'additional', 'refund']] = 'single'
    payment_status: Optional[Literal['completed', 'pending', 'cancelled', 'refunded']] = 'completed'
    payment_staff: Optional[str] = Field(None, max_length=50)
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=500)

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    payment_id: int
    payment_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentInDB(Payment):
    """데이터베이스 응답용 스키마"""
    pass
