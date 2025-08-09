from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
import pandas as pd

from core.database import get_db
from models.unreflected_customer import UnreflectedCustomer
from models.customer import Customer as CustomerModel
from schemas.customer import CustomerCreate
from schemas.response import PaginatedResponse, paginated_response
from utils.error_handlers import ErrorResponses, handle_database_error

router = APIRouter()

# 미반영 고객 스키마
from pydantic import BaseModel, ConfigDict
from datetime import date

class UnreflectedCustomerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_customer_id: Optional[int] = None
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    first_visit_date: Optional[date] = None
    region: Optional[str] = None
    referral_source: Optional[str] = None
    health_concerns: Optional[str] = None
    notes: Optional[str] = None
    assigned_staff: Optional[str] = None
    birth_year: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    occupation: Optional[str] = None
    data_source: Optional[str] = None
    import_date: Optional[datetime] = None
    import_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: str = "pending"

@router.get("", response_model=PaginatedResponse[UnreflectedCustomerSchema])
@router.get("/", response_model=PaginatedResponse[UnreflectedCustomerSchema])
def get_unreflected_customers(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    data_source: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """미반영 고객 목록 조회"""
    query = select(UnreflectedCustomer)

    # 검색 조건
    if search:
        query = query.where(
            (UnreflectedCustomer.name.contains(search)) |
            (UnreflectedCustomer.phone.contains(search))
        )

    # 필터
    if data_source:
        query = query.where(UnreflectedCustomer.data_source == data_source)

    if status:
        query = query.where(UnreflectedCustomer.status == status)

    # 정렬
    query = query.order_by(UnreflectedCustomer.created_at.desc())

    # 전체 개수
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()

    # 페이지네이션
    query = query.offset(skip).limit(limit)
    result = db.execute(query)
    customers = result.scalars().all()

    # 변환
    page = (skip // limit) + 1 if limit > 0 else 1
    customer_schemas = [UnreflectedCustomerSchema.model_validate(c) for c in customers]

    return paginated_response(
        data=customer_schemas,
        total=total,
        page=page,
        page_size=limit
    )

@router.get("/{customer_id}", response_model=UnreflectedCustomerSchema)
def get_unreflected_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """특정 미반영 고객 조회"""
    stmt = select(UnreflectedCustomer).where(UnreflectedCustomer.id == customer_id)
    result = db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise ErrorResponses.not_found("미반영 고객", customer_id)

    return customer

@router.post("/{customer_id}/move-back")
@handle_database_error
def move_customer_back(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """미반영 고객을 다시 정식 고객으로 이동"""
    # 미반영 고객 조회
    stmt = select(UnreflectedCustomer).where(UnreflectedCustomer.id == customer_id)
    result = db.execute(stmt)
    unreflected = result.scalar_one_or_none()

    if not unreflected:
        raise ErrorResponses.not_found("미반영 고객", customer_id)

    # 정식 고객으로 생성
    customer_data = {
        'name': unreflected.name,
        'phone': unreflected.phone,
        'email': unreflected.email,
        'first_visit_date': unreflected.first_visit_date,
        'region': unreflected.region,
        'referral_source': unreflected.referral_source,
        'health_concerns': unreflected.health_concerns,
        'notes': unreflected.notes,
        'assigned_staff': unreflected.assigned_staff,
        'birth_year': unreflected.birth_year,
        'gender': unreflected.gender,
        'address': unreflected.address,
        'emergency_contact': unreflected.emergency_contact,
        'occupation': unreflected.occupation,
        'membership_level': 'basic',
        'customer_status': 'active'
    }

    # None 값 제거
    customer_data = {k: v for k, v in customer_data.items() if v is not None}

    # 새 고객 생성
    new_customer = CustomerModel(**customer_data)
    db.add(new_customer)

    # 미반영 고객 상태 업데이트
    unreflected.status = "moved_back"

    db.commit()
    db.refresh(new_customer)

    return {
        "message": "고객이 정식 고객으로 이동되었습니다.",
        "customer_id": new_customer.customer_id
    }

@router.delete("/{customer_id}")
@handle_database_error
def delete_unreflected_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """미반영 고객 삭제"""
    stmt = select(UnreflectedCustomer).where(UnreflectedCustomer.id == customer_id)
    result = db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise ErrorResponses.not_found("미반영 고객", customer_id)

    # 상태를 rejected로 변경 (완전 삭제 대신)
    customer.status = "rejected"
    db.commit()

    return {"message": "미반영 고객이 거부 처리되었습니다."}

@router.get("/stats/summary")
def get_unreflected_stats(db: Session = Depends(get_db)):
    """미반영 고객 통계"""
    # 전체 개수
    total = db.query(UnreflectedCustomer).count()

    # 상태별 개수
    status_stats = db.query(
        UnreflectedCustomer.status,
        func.count(UnreflectedCustomer.id)
    ).group_by(UnreflectedCustomer.status).all()

    # 데이터 소스별 개수
    source_stats = db.query(
        UnreflectedCustomer.data_source,
        func.count(UnreflectedCustomer.id)
    ).filter(
        UnreflectedCustomer.status == 'pending'
    ).group_by(UnreflectedCustomer.data_source).all()

    return {
        "total": total,
        "by_status": {status: count for status, count in status_stats},
        "by_source": {source or "Unknown": count for source, count in source_stats}
    }

@router.post("/migrate-from-original")
@handle_database_error
def migrate_unreflected_customers(db: Session = Depends(get_db)):
    """원본 엑셀에 없는 모든 고객을 미반영 고객으로 이동"""
    # 원본 엑셀의 customer_id 목록
    excel_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장_전체고객.csv"
    df = pd.read_csv(excel_path, encoding='utf-8-sig')
    original_ids = df['번호'].tolist()

    # 원본에 없는 고객 조회
    unreflected = db.query(CustomerModel).filter(
        ~CustomerModel.customer_id.in_(original_ids)
    ).all()

    moved_count = 0

    for customer in unreflected:
        # 데이터 소스 추정
        created_date = customer.created_at.date()
        data_source = "Unknown"

        if created_date.strftime('%Y-%m-%d') == '2025-06-05':
            data_source = "초기 마이그레이션 (6/5)"
        elif created_date.strftime('%Y-%m-%d') == '2025-06-20':
            data_source = "2차 마이그레이션 (6/20)"
        elif created_date.strftime('%Y-%m-%d') == '2025-06-25':
            data_source = "월별 이용현황 import (6/25)"
        elif created_date >= pd.to_datetime('2025-06-26').date():
            data_source = "수동 입력 또는 테스트 데이터"

        # 이미 존재하는지 확인
        existing = db.query(UnreflectedCustomer).filter(
            UnreflectedCustomer.original_customer_id == customer.customer_id
        ).first()

        if not existing:
            unreflected_customer = UnreflectedCustomer(
                original_customer_id=customer.customer_id,
                name=customer.name,
                phone=customer.phone,
                email=customer.email,
                first_visit_date=customer.first_visit_date,
                region=customer.region,
                referral_source=customer.referral_source,
                health_concerns=customer.health_concerns,
                notes=customer.notes,
                assigned_staff=customer.assigned_staff,
                birth_year=customer.birth_year,
                gender=customer.gender,
                address=customer.address,
                emergency_contact=customer.emergency_contact,
                occupation=customer.occupation,
                data_source=data_source,
                status='pending'
            )
            db.add(unreflected_customer)
            moved_count += 1

    db.commit()

    return {
        "message": f"{moved_count}명의 고객을 미반영 고객 DB로 이동했습니다.",
        "total_unreflected": len(unreflected),
        "moved": moved_count,
        "customer_ids": [c.customer_id for c in unreflected]
    }
