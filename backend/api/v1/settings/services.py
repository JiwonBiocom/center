from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models import User, ServiceType
from core.auth import get_current_user
from schemas.service import ServiceTypeCreate, ServiceTypeUpdate, ServiceTypeResponse

router = APIRouter()

@router.get("", response_model=List[ServiceTypeResponse])
def get_service_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서비스 타입 목록 조회"""
    service_types = db.query(ServiceType).all()
    return service_types

@router.post("", response_model=ServiceTypeResponse)
def create_service_type(
    service_data: ServiceTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새 서비스 타입 생성 (관리자 전용)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    # 중복 확인
    existing = db.query(ServiceType).filter(
        ServiceType.service_name == service_data.service_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 서비스 타입입니다."
        )

    service_type = ServiceType(**service_data.dict())
    db.add(service_type)
    db.commit()
    db.refresh(service_type)

    return service_type

@router.put("/{service_type_id}")
def update_service_type(
    service_type_id: int,
    service_data: ServiceTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서비스 타입 수정 (관리자 전용)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    service_type = db.query(ServiceType).filter(
        ServiceType.service_type_id == service_type_id
    ).first()
    if not service_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="서비스 타입을 찾을 수 없습니다."
        )

    for key, value in service_data.dict(exclude_unset=True).items():
        setattr(service_type, key, value)

    db.commit()
    db.refresh(service_type)

    return {"message": "서비스 타입이 업데이트되었습니다.", "service_type": service_type}

@router.delete("/{service_type_id}")
def delete_service_type(
    service_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서비스 타입 삭제 (관리자 전용)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    service_type = db.query(ServiceType).filter(
        ServiceType.service_type_id == service_type_id
    ).first()
    if not service_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="서비스 타입을 찾을 수 없습니다."
        )

    # 사용 중인지 확인 (실제로는 더 복잡한 검증 필요)
    # TODO: ServiceUsage에서 사용 중인지 확인

    db.delete(service_type)
    db.commit()

    return {"message": "서비스 타입이 삭제되었습니다."}
