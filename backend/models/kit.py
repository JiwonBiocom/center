from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class KitType(Base):
    __tablename__ = "kit_types"
    
    kit_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    kit_managements = relationship("KitManagement", back_populates="kit_type_ref")

class KitManagement(Base):
    __tablename__ = "kit_management"
    
    kit_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    kit_type = Column(String(50), nullable=False)  # 기존 필드 유지
    kit_type_id = Column(Integer, ForeignKey("kit_types.kit_type_id"))  # 새로운 관계
    serial_number = Column(String(50), unique=True)
    received_date = Column(Date)
    result_received_date = Column(Date)
    result_delivered_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", backref="kits")
    kit_type_ref = relationship("KitType", back_populates="kit_managements")