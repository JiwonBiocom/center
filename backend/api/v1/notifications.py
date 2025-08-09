"""알림 API"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from core.auth import get_current_active_user
from models.user import User
from models.notification import NotificationType
from schemas.notification import (
    Notification,
    NotificationCreate,
    NotificationUpdate,
    NotificationStats,
    NotificationSettings,
    NotificationSettingsUpdate
)
from services.notification_service import NotificationService
from utils.error_handlers import ErrorResponses
from utils.response_formatter import ResponseFormatter

router = APIRouter()

# 슬래시 없는 경로도 처리 (redirect_slashes=False 대응)
@router.get("", response_model=List[Notification], include_in_schema=False)
def get_notifications_no_slash(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    notification_type: Optional[NotificationType] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 알림 목록 조회 (슬래시 없는 버전)"""
    return get_notifications(skip, limit, unread_only, notification_type, current_user, db)


@router.get("/", response_model=List[Notification])
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    notification_type: Optional[NotificationType] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 알림 목록 조회"""
    service = NotificationService(db)
    notifications = service.get_user_notifications(
        user_id=current_user.user_id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        notification_type=notification_type
    )
    return notifications


@router.get("/stats", response_model=NotificationStats)
def get_notification_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """알림 통계 조회"""
    service = NotificationService(db)
    stats = service.get_notification_stats(current_user.user_id)
    return stats


@router.post("/", response_model=Notification)
def create_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """알림 생성 (관리자 전용)"""
    if current_user.role not in ["admin", "manager"]:
        raise ErrorResponses.forbidden("관리자만 알림을 생성할 수 있습니다")

    service = NotificationService(db)

    # 사용자 ID가 없으면 현재 사용자로 설정
    if not notification.user_id:
        notification.user_id = current_user.user_id

    return service.create_notification(notification)


@router.post("/broadcast", response_model=dict)
def broadcast_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """전체 알림 발송 (관리자 전용)"""
    if current_user.role != "admin":
        raise ErrorResponses.forbidden("관리자만 전체 알림을 발송할 수 있습니다")

    service = NotificationService(db)

    # 모든 활성 사용자 조회
    from sqlalchemy import select
    user_query = select(User.user_id).where(User.is_active == True)
    result = db.execute(user_query)
    user_ids = [row[0] for row in result.all()]

    # 대량 알림 생성
    notifications = service.create_bulk_notifications(user_ids, notification)

    return ResponseFormatter.success({
        "message": f"{len(notifications)}명에게 알림이 발송되었습니다",
        "count": len(notifications)
    })


@router.patch("/{notification_id}", response_model=Notification)
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """알림 읽음 처리"""
    service = NotificationService(db)
    return service.mark_as_read(notification_id, current_user.user_id)


@router.post("/mark-all-read", response_model=dict)
def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """모든 알림 읽음 처리"""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.user_id)

    return ResponseFormatter.success({
        "message": f"{count}개의 알림을 읽음 처리했습니다",
        "count": count
    })


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """알림 삭제"""
    service = NotificationService(db)
    service.delete_notification(notification_id, current_user.user_id)
    return ResponseFormatter.deleted("알림이 삭제되었습니다")


# 알림 설정 관련 엔드포인트

@router.get("/settings", response_model=NotificationSettings)
def get_notification_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """알림 설정 조회"""
    service = NotificationService(db)
    return service.get_or_create_settings(current_user.user_id)


@router.put("/settings", response_model=NotificationSettings)
def update_notification_settings(
    settings: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """알림 설정 수정"""
    service = NotificationService(db)
    return service.update_settings(
        current_user.user_id,
        settings.model_dump(exclude_unset=True)
    )


# 테스트용 엔드포인트
@router.post("/test", response_model=Notification)
def create_test_notification(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """테스트 알림 생성"""
    service = NotificationService(db)

    test_notification = NotificationCreate(
        user_id=current_user.user_id,
        type=NotificationType.SYSTEM,
        title="테스트 알림",
        message="이것은 테스트 알림입니다. 알림 시스템이 정상적으로 작동하고 있습니다.",
        priority="medium",
        action_url="/notifications"
    )

    return service.create_notification(test_notification)


@router.post("/test/package-expiry")
def test_package_expiry_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """패키지 만료 알림 테스트 (관리자 전용)"""
    if current_user.role != "admin":
        raise ErrorResponses.forbidden("관리자만 테스트할 수 있습니다")

    from services.scheduled_tasks import ScheduledTasks

    try:
        ScheduledTasks.check_package_expiry()
        return ResponseFormatter.success({
            "message": "패키지 만료 알림 작업이 실행되었습니다"
        })
    except Exception as e:
        raise ErrorResponses.business_logic_error(f"작업 실행 중 오류: {str(e)}")
