from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class InBodyRecord(Base):
    __tablename__ = "inbody_records"
    
    record_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    
    # 인바디 측정 정보
    measurement_date = Column(DateTime, nullable=False, default=func.now())
    
    # 기본 신체 정보
    weight = Column(Float, nullable=True, comment="체중 (kg)")
    body_fat_percentage = Column(Float, nullable=True, comment="체지방률 (%)")
    skeletal_muscle_mass = Column(Float, nullable=True, comment="골격근량 (kg)")
    extracellular_water_ratio = Column(Float, nullable=True, comment="세포외수분비")
    phase_angle = Column(Float, nullable=True, comment="위상각")
    visceral_fat_level = Column(Integer, nullable=True, comment="내장지방 레벨")
    
    # 추가 메모
    notes = Column(Text, nullable=True, comment="측정 관련 메모")
    measured_by = Column(String(100), nullable=True, comment="측정자")
    
    # 타임스탬프
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 관계
    customer = relationship("Customer", back_populates="inbody_records")
    
    def __repr__(self):
        return f"<InBodyRecord(customer_id={self.customer_id}, measurement_date={self.measurement_date})>"