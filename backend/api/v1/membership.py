"""
회원 등급 관리 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from typing import Dict, Any
import json
from datetime import datetime

from core.database import get_db
from core.auth import get_current_user
from models.user import User
from models.system import SystemSettings

router = APIRouter(
    prefix="/membership",
    tags=["membership"]
)

@router.get("/criteria")
async def get_membership_criteria(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """현재 회원 등급 기준 조회"""
    query = select(SystemSettings).where(SystemSettings.setting_key == "membership_criteria")
    result = db.execute(query)
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원 등급 기준이 설정되지 않았습니다."
        )
    
    return json.loads(setting.setting_value)

@router.put("/criteria")
async def update_membership_criteria(
    criteria: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """회원 등급 기준 업데이트 (관리자 전용)"""
    # 관리자 권한 체크
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    
    # 필수 등급 확인
    required_levels = ["bronze", "silver", "gold", "platinum"]
    for level in required_levels:
        if level not in criteria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{level} 등급 기준이 누락되었습니다."
            )
    
    # 기존 설정 조회
    query = select(SystemSettings).where(SystemSettings.setting_key == "membership_criteria")
    result = db.execute(query)
    setting = result.scalar_one_or_none()
    
    if setting:
        # 업데이트
        setting.setting_value = json.dumps(criteria, ensure_ascii=False)
        setting.updated_at = datetime.now()
    else:
        # 새로 생성
        setting = SystemSettings(
            setting_key="membership_criteria",
            setting_value=json.dumps(criteria, ensure_ascii=False),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(setting)
    
    db.commit()
    
    return {"message": "회원 등급 기준이 업데이트되었습니다.", "criteria": criteria}

@router.get("/status-descriptions")
async def get_status_descriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 상태 및 위험 수준 설명 조회"""
    query = select(SystemSettings).where(SystemSettings.setting_key == "customer_status_descriptions")
    result = db.execute(query)
    setting = result.scalar_one_or_none()
    
    if not setting:
        # 기본값 반환
        return {
            "customer_status": {
                "active": {
                    "name": "활성",
                    "description": "최근 30일 이내 서비스 이용",
                    "color": "green"
                },
                "inactive": {
                    "name": "비활성",
                    "description": "30일~90일 동안 서비스 미이용",
                    "color": "yellow"
                },
                "dormant": {
                    "name": "휴면",
                    "description": "90일 이상 서비스 미이용",
                    "color": "red"
                }
            }
        }
    
    return json.loads(setting.setting_value)

@router.post("/update-all-customers")
async def update_all_customers_membership(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """모든 고객의 등급/상태 일괄 업데이트 (관리자 전용)"""
    # 관리자 권한 체크
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    
    # 회원 등급 기준 조회
    query = select(SystemSettings).where(SystemSettings.setting_key == "membership_criteria")
    result = db.execute(query)
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원 등급 기준이 설정되지 않았습니다."
        )
    
    criteria = json.loads(setting.setting_value)
    
    # 모든 고객 조회 및 업데이트
    from models.customer import Customer
    customers = db.query(Customer).all()
    
    updated_count = 0
    for customer in customers:
        # 고객 상태 업데이트
        customer.update_customer_status()
        
        # 회원 등급 업데이트
        customer.update_membership_level(criteria)
        
        
        updated_count += 1
    
    db.commit()
    
    return {
        "message": f"{updated_count}명의 고객 정보가 업데이트되었습니다.",
        "updated_count": updated_count
    }