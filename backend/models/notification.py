"""알림 모델"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum


class NotificationType(str, enum.Enum):
    """알림 타입"""
    PACKAGE = "package"
    KIT = "kit"
    APPOINTMENT = "appointment"
    SYSTEM = "system"
    PAYMENT = "payment"
    CUSTOMER = "customer"


class NotificationPriority(str, enum.Enum):
    """알림 우선순위"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Notification(Base):
    """알림 테이블"""
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    is_sent = Column(Boolean, default=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    action_url = Column(String(500))  # 클릭 시 이동할 URL
    related_id = Column(Integer)  # 관련 객체 ID (package_id, customer_id 등)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    read_at = Column(DateTime, nullable=True)
    scheduled_for = Column(DateTime, nullable=True, index=True)  # 예약 발송 시간
    
    # Relationships
    user = relationship("User", backref="notifications")


class NotificationSettings(Base):
    """사용자별 알림 설정"""
    __tablename__ = "notification_settings"
    
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    
    # 알림 타입별 설정
    package_alerts = Column(Boolean, default=True)
    appointment_reminders = Column(Boolean, default=True)
    payment_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    marketing_notifications = Column(Boolean, default=False)
    
    # 방해 금지 설정
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # "22:00"
    quiet_hours_end = Column(String(5))    # "08:00"
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="notification_settings", uselist=False)