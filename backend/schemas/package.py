from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class PackageBase(BaseModel):
    package_name: str = Field(..., max_length=100)
    total_sessions: Optional[int] = None
    price: Optional[Decimal] = Field(None, decimal_places=2)
    valid_days: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True

class PackageCreate(PackageBase):
    pass

class Package(PackageBase):
    package_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PackagePurchaseBase(BaseModel):
    customer_id: int
    package_id: int
    purchase_date: date
    expiry_date: Optional[date] = None
    total_sessions: Optional[int] = None
    used_sessions: int = 0
    remaining_sessions: Optional[int] = None

class PackagePurchaseCreate(PackagePurchaseBase):
    pass

class PackagePurchase(PackagePurchaseBase):
    purchase_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True