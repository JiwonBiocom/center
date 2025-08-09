from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List

from core.database import get_db
from models import User, NotificationPreferences
from core.auth import get_current_user

router = APIRouter()

@router.get("/preferences")
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """알림 설정 조회"""
    preferences = db.query(NotificationPreferences).filter(
        NotificationPreferences.user_id == current_user.user_id
    ).all()

    # 기본 설정
    default_types = [
        "package_expiry",
        "payment_received",
        "new_customer",
        "service_completed"
    ]

    pref_dict = {p.notification_type: p for p in preferences}
    result = []

    for ntype in default_types:
        if ntype in pref_dict:
            result.append(pref_dict[ntype])
        else:
            result.append({
                "notification_type": ntype,
                "in_app": True,
                "email": False,
                "sms": False
            })

    return result

@router.put("/preferences")
def update_notification_preferences(
    preferences: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """알림 설정 업데이트"""
    for pref in preferences:
        existing = db.query(NotificationPreferences).filter(
            and_(
                NotificationPreferences.user_id == current_user.user_id,
                NotificationPreferences.notification_type == pref["notification_type"]
            )
        ).first()

        if existing:
            existing.in_app = pref.get("in_app", True)
            existing.email = pref.get("email", False)
            existing.sms = pref.get("sms", False)
        else:
            new_pref = NotificationPreferences(
                user_id=current_user.user_id,
                notification_type=pref["notification_type"],
                in_app=pref.get("in_app", True),
                email=pref.get("email", False),
                sms=pref.get("sms", False)
            )
            db.add(new_pref)

    db.commit()
    return {"message": "알림 설정이 업데이트되었습니다."}
