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
    existing = db.query(CustomerPreference).filter(
        CustomerPreference.customer_id == customer_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 선호도 정보가 존재합니다. PUT 메서드를 사용하세요."
        )
    
    # 새 선호도 생성
    new_preference = CustomerPreference(
        customer_id=customer_id,
        preferred_services=preferences.preferred_services or [],
        preferred_time=preferences.preferred_time,
        preferred_intensity=preferences.preferred_intensity,
        health_interests=preferences.health_interests or [],
        communication_preference=preferences.communication_preference,
        marketing_consent=preferences.marketing_consent or False
    )
    
    db.add(new_preference)
    db.commit()
    db.refresh(new_preference)
    
    return {
        "message": "선호도가 성공적으로 생성되었습니다.",
        "data": {"preference_id": new_preference.preference_id}
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
    existing = db.query(CustomerPreference).filter(
        CustomerPreference.customer_id == customer_id
    ).first()
    
    if not existing:
        # 선호도가 없으면 새로 생성
        new_preference = CustomerPreference(
            customer_id=customer_id,
            preferred_services=preferences.preferred_services or [],
            preferred_time=preferences.preferred_time,
            preferred_intensity=preferences.preferred_intensity,
            health_interests=preferences.health_interests or [],
            communication_preference=preferences.communication_preference,
            marketing_consent=preferences.marketing_consent or False
        )
        db.add(new_preference)
        db.commit()
        db.refresh(new_preference)
        
        return {
            "message": "선호도가 성공적으로 생성되었습니다.",
            "data": {"preference_id": new_preference.preference_id}
        }
    
    # 기존 선호도 업데이트
    if preferences.preferred_services is not None:
        existing.preferred_services = preferences.preferred_services
    
    if preferences.preferred_time is not None:
        existing.preferred_time = preferences.preferred_time
    
    if preferences.preferred_intensity is not None:
        existing.preferred_intensity = preferences.preferred_intensity
    
    if preferences.health_interests is not None:
        existing.health_interests = preferences.health_interests
    
    if preferences.communication_preference is not None:
        existing.communication_preference = preferences.communication_preference
    
    if preferences.marketing_consent is not None:
        existing.marketing_consent = preferences.marketing_consent
    
    db.commit()
    db.refresh(existing)
    
    return {
        "message": "선호도가 성공적으로 업데이트되었습니다.",
        "data": {"preference_id": existing.preference_id}
    }
