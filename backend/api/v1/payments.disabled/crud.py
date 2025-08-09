from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date, timedelta

from core.database import get_db
from models.payment import Payment as PaymentModel
from models.customer import Customer as CustomerModel
from models.package import Package as PackageModel, PackagePurchase as PackagePurchaseModel
from schemas.payment import Payment, PaymentCreate

router = APIRouter()

@router.post("/", response_model=Payment)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    """결제 등록"""
    # 고객 확인
    customer_query = select(CustomerModel).where(CustomerModel.customer_id == payment.customer_id)
    customer_result = db.execute(customer_query)
    customer = customer_result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="고객을 찾을 수 없습니다.")
    
    # 결제 생성
    db_payment = PaymentModel(**payment.model_dump())
    db.add(db_payment)
    
    # 패키지 구매 처리 (패키지 ID가 제공된 경우)
    if hasattr(payment, 'package_id') and payment.package_id:
        package_query = select(PackageModel).where(PackageModel.package_id == payment.package_id)
        package_result = db.execute(package_query)
        package = package_result.scalar_one_or_none()
        
        if package:
            # 패키지 구매 레코드 생성
            purchase = PackagePurchaseModel(
                customer_id=payment.customer_id,
                package_id=payment.package_id,
                purchase_date=payment.payment_date,
                expiry_date=payment.payment_date + timedelta(days=package.valid_days),
                total_sessions=package.total_sessions,
                used_sessions=0,
                remaining_sessions=package.total_sessions
            )
            db.add(purchase)
    
    db.commit()
    db.refresh(db_payment)
    
    return db_payment

@router.get("/", response_model=List[dict])
def get_payments(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    customer_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """결제 내역 조회"""
    query = select(
        PaymentModel,
        CustomerModel.name.label('customer_name'),
        CustomerModel.phone.label('customer_phone')
    ).join(
        CustomerModel, PaymentModel.customer_id == CustomerModel.customer_id
    )
    
    # 필터링
    if date_from:
        query = query.where(PaymentModel.payment_date >= date_from)
    if date_to:
        query = query.where(PaymentModel.payment_date <= date_to)
    if customer_id:
        query = query.where(PaymentModel.customer_id == customer_id)
    if payment_method:
        query = query.where(PaymentModel.payment_method == payment_method)
    
    # 정렬 및 페이지네이션
    query = query.order_by(PaymentModel.payment_date.desc(), PaymentModel.payment_id.desc())
    query = query.offset(skip).limit(limit)
    
    result = db.execute(query)
    rows = result.all()
    
    # 결과 포맷팅
    payments = []
    for row in rows:
        payment = row[0]
        payment_dict = {
            "payment_id": payment.payment_id,
            "customer_id": payment.customer_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "payment_date": payment.payment_date.isoformat(),
            "amount": float(payment.amount),
            "payment_method": payment.payment_method,
            "card_holder_name": payment.card_holder_name,
            "approval_number": payment.approval_number,
            "payment_staff": payment.payment_staff,
            "purchase_type": payment.purchase_type,
            "purchase_order": payment.purchase_order,
            "created_at": payment.created_at.isoformat()
        }
        payments.append(payment_dict)
    
    return payments

@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """결제 취소 (삭제)"""
    # 결제 확인
    query = select(PaymentModel).where(PaymentModel.payment_id == payment_id)
    result = db.execute(query)
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="결제 내역을 찾을 수 없습니다.")
    
    # 관련 패키지 구매 내역도 확인하고 삭제 필요 시 처리
    # (실제로는 soft delete나 취소 상태로 변경하는 것이 좋음)
    
    db.delete(payment)
    db.commit()
    
    return {"message": "결제가 취소되었습니다."}