from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class ServiceType(Base):
    __tablename__ = "service_types"
    
    service_type_id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(20), nullable=False, unique=True)
    description = Column(Text)
    default_duration = Column(Integer, default=60)
    default_price = Column(Integer, default=0)
    service_color = Column(String(10), default="#3B82F6")

class ServiceUsage(Base):
    __tablename__ = "service_usage"
    
    usage_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    service_date = Column(Date, nullable=False, index=True)
    service_type_id = Column(Integer, ForeignKey("service_types.service_type_id"))
    package_id = Column(Integer, ForeignKey("packages.package_id"))
    session_details = Column(Text)
    session_number = Column(Integer)
    created_by = Column(String(50))
    # reservation_id = Column(Integer, ForeignKey("reservations.reservation_id"), nullable=True)  # 예약과 연결
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", backref="service_usages")
    service_type = relationship("ServiceType", backref="usages")
    package = relationship("Package", backref="usages")
    # reservation = relationship("Reservation", backref="service_usage")