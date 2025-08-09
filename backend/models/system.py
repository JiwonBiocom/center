from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Time, JSON
from sqlalchemy.sql import func
from core.database import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    setting_id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(50), unique=True, nullable=False)
    setting_value = Column(Text)
    setting_type = Column(String(20))  # string, number, boolean, json
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class CompanyInfo(Base):
    __tablename__ = "company_info"
    
    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    business_hours = Column(JSON)  # {"mon": {"open": "09:00", "close": "18:00"}, ...}
    holidays = Column(JSON)  # ["2025-01-01", "2025-02-08", ...]
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"
    
    preference_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    notification_type = Column(String(50))  # package_expiry, payment_received, etc.
    in_app = Column(Boolean, default=True)
    email = Column(Boolean, default=False)
    sms = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())