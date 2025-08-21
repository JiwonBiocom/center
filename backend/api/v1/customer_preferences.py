"""
고객 선호도 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from core.database import get_db
from core.auth import get_current_user
from models.user import User
from models.customer_extended import CustomerPreference

router = APIRouter(prefix="/customers/{customer_id}/preferences", tags=["customer-preferences"])

class CustomerPreferencesCreate(BaseModel):
    preferred_services: Optional[List[str]] = []
    preferred_time: Optional[str] = None
    preferred_intensity: Optional[str] = None
    health_interests: Optional[List[str]] = []
    communication_preference: Optional[str] = None
    marketing_consent: Optional[bool] = False

class CustomerPreferencesUpdate(BaseModel):
    preferred_services: Optional[List[str]] = None
    preferred_time: Optional[str] = None
    preferred_intensity: Optional[str] = None
    health_interests: Optional[List[str]] = None
    communication_preference: Optional[str] = None
    marketing_consent: Optional[bool] = None

@router.get("")
@router.get("/")
async def get_customer_preferences(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 선호도 조회"""
    preference = db.query(CustomerPreference).filter(CustomerPreference.customer_id == customer_id).first()
    
    if not preference:
        return {"message": "선호도 정보가 없습니다.", "data": None}
    
    return {
        "data": {
            "preference_id": preference.preference_id,
            "customer_id": preference.customer_id,
            "preferred_services": preference.preferred_services or [],
            "preferred_time": preference.preferred_time,
            "preferred_intensity": preference.preferred_intensity,
            "health_interests": preference.health_interests or [],
            "communication_preference": preference.communication_preference,
            "marketing_consent": preference.marketing_consent,
            "created_at": preference.created_at.isoformat() if preference.created_at else None,
            "updated_at": preference.updated_at.isoformat() if preference.updated_at else None
        }
    }

@router.post("")
@router.post("/")
async def create_customer_preferences(
    customer_id: int,
    preferences: CustomerPreferencesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 선호도 생성"""
    # 기존 선호도 확인
    check_query = text("""
        SELECT preference_id FROM customer_preferences
        WHERE customer_id = :customer_id
        LIMIT 1
    """)
    
    existing = db.execute(check_query, {"customer_id": customer_id}).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 선호도 정보가 존재합니다. PUT 메서드를 사용하세요."
        )
    
    # 새 선호도 생성
    insert_query = text("""
        INSERT INTO customer_preferences (
            customer_id,
            preferred_services,
            preferred_time,
            preferred_intensity,
            health_interests,
            communication_preference,
            marketing_consent,
            created_at,
            updated_at
        ) VALUES (
            :customer_id,
            :preferred_services,
            :preferred_time,
            :preferred_intensity,
            :health_interests,
            :communication_preference,
            :marketing_consent,
            NOW(),
            NOW()
        )
        RETURNING preference_id
    """)
    
    result = db.execute(insert_query, {
        "customer_id": customer_id,
        "preferred_services": preferences.preferred_services,
        "preferred_time": preferences.preferred_time,
        "preferred_intensity": preferences.preferred_intensity,
        "health_interests": preferences.health_interests,
        "communication_preference": preferences.communication_preference,
        "marketing_consent": preferences.marketing_consent
    })
    
    db.commit()
    preference_id = result.scalar()
    
    return {
        "message": "선호도가 성공적으로 생성되었습니다.",
        "data": {"preference_id": preference_id}
    }

@router.put("")
@router.put("/")
async def update_customer_preferences(
    customer_id: int,
    preferences: CustomerPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 선호도 수정"""
    # 기존 선호도 확인
    check_query = text("""
        SELECT preference_id FROM customer_preferences
        WHERE customer_id = :customer_id
        LIMIT 1
    """)
    
    existing = db.execute(check_query, {"customer_id": customer_id}).first()
    if not existing:
        # 선호도가 없으면 새로 생성
        insert_query = text("""
            INSERT INTO customer_preferences (
                customer_id,
                preferred_services,
                preferred_time,
                preferred_intensity,
                health_interests,
                communication_preference,
                marketing_consent,
                created_at,
                updated_at
            ) VALUES (
                :customer_id,
                :preferred_services,
                :preferred_time,
                :preferred_intensity,
                :health_interests,
                :communication_preference,
                :marketing_consent,
                NOW(),
                NOW()
            )
            RETURNING preference_id
        """)
        
        result = db.execute(insert_query, {
            "customer_id": customer_id,
            "preferred_services": preferences.preferred_services or [],
            "preferred_time": preferences.preferred_time,
            "preferred_intensity": preferences.preferred_intensity,
            "health_interests": preferences.health_interests or [],
            "communication_preference": preferences.communication_preference,
            "marketing_consent": preferences.marketing_consent or False
        })
        
        db.commit()
        preference_id = result.scalar()
        
        return {
            "message": "선호도가 성공적으로 생성되었습니다.",
            "data": {"preference_id": preference_id}
        }
    
    # 기존 선호도 업데이트
    update_fields = []
    update_params = {"customer_id": customer_id}
    
    if preferences.preferred_services is not None:
        update_fields.append("preferred_services = :preferred_services")
        update_params["preferred_services"] = preferences.preferred_services
    
    if preferences.preferred_time is not None:
        update_fields.append("preferred_time = :preferred_time")
        update_params["preferred_time"] = preferences.preferred_time
    
    if preferences.preferred_intensity is not None:
        update_fields.append("preferred_intensity = :preferred_intensity")
        update_params["preferred_intensity"] = preferences.preferred_intensity
    
    if preferences.health_interests is not None:
        update_fields.append("health_interests = :health_interests")
        update_params["health_interests"] = preferences.health_interests
    
    if preferences.communication_preference is not None:
        update_fields.append("communication_preference = :communication_preference")
        update_params["communication_preference"] = preferences.communication_preference
    
    if preferences.marketing_consent is not None:
        update_fields.append("marketing_consent = :marketing_consent")
        update_params["marketing_consent"] = preferences.marketing_consent
    
    if update_fields:
        update_fields.append("updated_at = NOW()")
        update_query = text(f"""
            UPDATE customer_preferences
            SET {', '.join(update_fields)}
            WHERE customer_id = :customer_id
        """)
        
        db.execute(update_query, update_params)
        db.commit()
    
    return {
        "message": "선호도가 성공적으로 업데이트되었습니다.",
        "data": {"preference_id": existing.preference_id}
    }
