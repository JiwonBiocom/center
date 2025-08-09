from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .customer import Customer

# KitType Schemas
class KitTypeBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    price: int
    is_active: bool = True

class KitTypeCreate(KitTypeBase):
    pass

class KitTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    is_active: Optional[bool] = None

class KitType(KitTypeBase):
    model_config = ConfigDict(from_attributes=True)
    
    kit_type_id: int
    created_at: datetime
    updated_at: datetime

# KitManagement Schemas
class KitManagementBase(BaseModel):
    customer_id: int
    kit_type_id: int
    serial_number: Optional[str] = None
    received_date: Optional[date] = None
    result_received_date: Optional[date] = None
    result_delivered_date: Optional[date] = None

class KitManagementCreate(KitManagementBase):
    pass

class KitManagementUpdate(BaseModel):
    customer_id: Optional[int] = None
    kit_type_id: Optional[int] = None
    serial_number: Optional[str] = None
    received_date: Optional[date] = None
    result_received_date: Optional[date] = None
    result_delivered_date: Optional[date] = None

class KitManagement(KitManagementBase):
    model_config = ConfigDict(from_attributes=True)
    
    kit_id: int
    kit_type: str  # 기존 필드 유지
    created_at: datetime
    
    # Relations
    customer: Optional[dict] = None
    kit_type_ref: Optional[KitType] = None

class KitManagementWithRelations(KitManagement):
    customer: Optional[dict] = None

# List Response
class KitManagementListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    kits: List[KitManagement]
    total: int
    page: int
    page_size: int

class KitTypeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    kit_types: List[KitType]
    total: int