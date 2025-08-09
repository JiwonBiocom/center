from sqlalchemy import Column, Integer, String, Date, DateTime, Time, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class StaffSchedule(Base):
    __tablename__ = "staff_schedules"
    
    schedule_id = Column(Integer, primary_key=True, index=True)
    week_start_date = Column(Date, nullable=False, index=True)
    schedule_data = Column(Text, nullable=False)  # JSON 형태로 저장
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))