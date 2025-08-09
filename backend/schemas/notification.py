"""알림 스키마"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """알림 타입"""
    PACKAGE = "package"
    KIT = "kit"
    APPOINTMENT = "appointment"
    SYSTEM = "system"
    PAYMENT = "payment"
    CUSTOMER = "customer"


class NotificationPriority(str, Enum):
    """알림 우선순위"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NotificationBase(BaseModel):
    """알림 기본 스키마"""
    type: NotificationType
    title: str = Field(..., max_length=200)
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    action_url: Optional[str] = Field(None, max_length=500)
    related_id: Optional[int] = None
    scheduled_for: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    """알림 생성 스키마"""
    user_id: Optional[int] = None  # None이면 전체 알림


class NotificationUpdate(BaseModel):
    """알림 수정 스키마"""
    is_read: Optional[bool] = None


class Notification(NotificationBase):
    """알림 응답 스키마"""
    notification_id: int
    user_id: Optional[int]
    is_read: bool
    is_sent: bool
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class NotificationSettingsBase(BaseModel):
    """알림 설정 기본 스키마"""
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    package_alerts: bool = True
    appointment_reminders: bool = True
    payment_notifications: bool = True
    system_notifications: bool = True
    marketing_notifications: bool = False
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")


class NotificationSettingsUpdate(NotificationSettingsBase):
    """알림 설정 수정 스키마"""
    pass


class NotificationSettings(NotificationSettingsBase):
    """알림 설정 응답 스키마"""
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationStats(BaseModel):
    """알림 통계"""
    total: int
    unread: int
    by_type: dict[NotificationType, int]
    by_priority: dict[NotificationPriority, int]