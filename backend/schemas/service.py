from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class ServiceTypeBase(BaseModel):
    service_name: str = Field(..., max_length=20)
    description: Optional[str] = None
    default_duration: Optional[int] = 60
    default_price: Optional[int] = 0
    service_color: Optional[str] = "#3B82F6"

class ServiceType(ServiceTypeBase):
    service_type_id: int
    
    class Config:
        from_attributes = True

class ServiceUsageBase(BaseModel):
    customer_id: int
    service_date: date
    service_type_id: int
    package_id: Optional[int] = None
    session_details: Optional[str] = None
    session_number: Optional[int] = None
    created_by: Optional[str] = Field(None, max_length=50)

class ServiceUsageCreate(ServiceUsageBase):
    pass

class ServiceUsage(ServiceUsageBase):
    usage_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ServiceTypeCreate(ServiceTypeBase):
    pass

class ServiceTypeUpdate(BaseModel):
    service_name: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    default_duration: Optional[int] = None
    default_price: Optional[int] = None
    service_color: Optional[str] = None

class ServiceTypeResponse(ServiceTypeBase):
    service_type_id: int
    
    class Config:
        from_attributes = True