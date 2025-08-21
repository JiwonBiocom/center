from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, text
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from core.database import get_db
from core.auth import get_current_user
from models.package import Package as PackageModel, PackagePurchase as PackagePurchaseModel
from models.customer import Customer as CustomerModel
from models.payment import Payment as PaymentModel
from models.user import User
from schemas.package import Package, PackageCreate
from utils.response_formatter import ResponseFormatter
import logging

logger = logging.getLogger(__name__)

class PackagePurchaseRequest(BaseModel):
    customer_id: int
    package_id: int
    payment_amount: int
    payment_method: str
    staff_memo: Optional[str] = None
    purchase_date: str
    start_date: str
    end_date: str

class PackageUpdateRequest(BaseModel):
    """Frontend-compatible package update model"""
    package_name: Optional[str] = None
    total_sessions: Optional[int] = None
    price: Optional[int] = None  # Frontend uses 'price'
    valid_days: Optional[int] = None  # Frontend uses 'valid_days'
    description: Optional[str] = None
    is_active: Optional[bool] = None

router = APIRouter()

@router.get("/available")
async def get_available_packages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """구매 가능한 패키지 목록 조회"""
    try:
        query = text("""
            SELECT
                package_id,
                package_name,
                base_price as price,
                valid_months,
                total_sessions,
                description,
                is_active
            FROM packages
            WHERE is_active = true
            ORDER BY package_id
        """)

        result = db.execute(query).all()

        packages = []
        for row in result:
            packages.append({
                "package_id": row.package_id,
                "package_name": row.package_name,
                "price": row.price,
                "valid_days": row.valid_months * 30,  # Convert months to days
                "total_sessions": row.total_sessions or 0,
                "description": row.description
            })

        response = ResponseFormatter.success(
            data=packages,
            message="패키지 목록을 성공적으로 조회했습니다."
        )
        return response.model_dump()

    except Exception as e:
        logger.error(f"Error getting available packages: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"패키지 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/purchase")
async def purchase_package(
    purchase_data: PackagePurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """패키지 구매 처리"""
    try:
        logger.info(f"Processing package purchase for customer {purchase_data.customer_id}")

        # 1. 고객 존재 확인
        customer_query = text("SELECT customer_id, name FROM customers WHERE customer_id = :customer_id")
        customer_result = db.execute(customer_query, {"customer_id": purchase_data.customer_id}).first()

        if not customer_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="고객을 찾을 수 없습니다."
            )

        # 2. 패키지 정보 조회
        package_query = text("""
            SELECT
                package_id, package_name, base_price as price, valid_months,
                total_sessions, description,
                is_active
            FROM packages
            WHERE package_id = :package_id AND is_active = true
        """)
        package_result = db.execute(package_query, {"package_id": purchase_data.package_id}).first()

        if not package_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="패키지를 찾을 수 없습니다."
            )

        # 3. 결제 기록 생성
        payment_insert = text("""
            INSERT INTO payments (
                customer_id, amount, payment_method, payment_date,
                purchase_type, payment_staff, memo
            ) VALUES (
                :customer_id, :amount, :payment_method, :payment_date,
                :purchase_type, :payment_staff, :memo
            ) RETURNING payment_id
        """)

        payment_memo = f"{package_result.package_name} 패키지 구매"
        if purchase_data.staff_memo:
            payment_memo += f" - {purchase_data.staff_memo}"

        payment_result = db.execute(payment_insert, {
            "customer_id": purchase_data.customer_id,
            "amount": purchase_data.payment_amount,
            "payment_method": purchase_data.payment_method,
            "payment_date": datetime.fromisoformat(purchase_data.purchase_date.replace('Z', '+00:00')),
            "purchase_type": "패키지",
            "payment_staff": current_user.name,
            "memo": payment_memo
        }).first()

        payment_id = payment_result.payment_id

        # 4. 패키지 구매 기록 생성
        package_purchase_insert = text("""
            INSERT INTO package_purchases (
                customer_id, package_id, purchase_date, expiry_date,
                total_sessions, used_sessions, remaining_sessions
            ) VALUES (
                :customer_id, :package_id, :purchase_date, :expiry_date,
                :total_sessions, 0, :total_sessions
            ) RETURNING purchase_id
        """)

        purchase_result = db.execute(package_purchase_insert, {
            "customer_id": purchase_data.customer_id,
            "package_id": purchase_data.package_id,
            "purchase_date": datetime.fromisoformat(purchase_data.purchase_date.replace('Z', '+00:00')),
            "expiry_date": datetime.fromisoformat(purchase_data.end_date.replace('Z', '+00:00')),
            "total_sessions": package_result.total_sessions
        }).first()

        db.commit()

        logger.info(f"Package purchase completed: purchase_id={purchase_result.purchase_id}, payment_id={payment_id}")

        response = ResponseFormatter.created(
            data={
                "purchase_id": purchase_result.purchase_id,
                "payment_id": payment_id,
                "customer_name": customer_result.name,
                "package_name": package_result.package_name,
                "total_sessions": package_result.total_sessions,
                "purchase_amount": purchase_data.payment_amount
            },
            message="패키지 구매가 성공적으로 완료되었습니다."
        )
        return response.model_dump()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error purchasing package: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"패키지 구매 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/", response_model=List[Package])
def get_packages(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """패키지 목록 조회"""
    try:
        query = select(PackageModel)
        if is_active is not None:
            query = query.where(PackageModel.is_active == is_active)

        query = query.order_by(PackageModel.package_id)

        result = db.execute(query)
        return result.scalars().all()
    except Exception as e:
        print(f"패키지 조회 에러 상세: {str(e)}")
        print(f"에러 타입: {type(e)}")
        # 빈 리스트 반환하여 서버가 죽지 않도록
        return []

# @router.post("/", response_model=Package)
@router.post("", response_model=Package)
def create_package(
    package: PackageCreate,
    db: Session = Depends(get_db)
):
    """패키지 생성"""
    db_package = PackageModel(**package.model_dump())
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package

# @router.put("/{package_id}", response_model=Package)
@router.put("/{package_id}/")
def update_package(
    package_id: int,
    package_update: PackageUpdateRequest,
    db: Session = Depends(get_db)
):
    """패키지 수정"""
    query = select(PackageModel).where(PackageModel.package_id == package_id)
    result = db.execute(query)
    db_package = result.scalar_one_or_none()

    if not db_package:
        raise HTTPException(status_code=404, detail="패키지를 찾을 수 없습니다.")

    # Update fields with proper mapping
    update_data = package_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == 'price' and value is not None:
            # Map 'price' to 'base_price'
            db_package.base_price = value
        elif key == 'valid_days' and value is not None:
            # Convert days to months and map to 'valid_months'
            db_package.valid_months = value // 30
        elif hasattr(db_package, key):
            # Other fields can be set directly
            setattr(db_package, key, value)

    db.commit()
    db.refresh(db_package)
    
    # Return response in frontend-compatible format
    return {
        "package_id": db_package.package_id,
        "package_name": db_package.package_name,
        "total_sessions": db_package.total_sessions,
        "price": db_package.base_price,  # Map base_price to price
        "valid_days": db_package.valid_months * 30 if db_package.valid_months else None,  # Convert months to days
        "description": db_package.description,
        "is_active": db_package.is_active,
        "created_at": db_package.created_at
    }

@router.delete("/{package_id}")
def delete_package(
    package_id: int,
    db: Session = Depends(get_db)
):
    """패키지 비활성화"""
    query = select(PackageModel).where(PackageModel.package_id == package_id)
    result = db.execute(query)
    package = result.scalar_one_or_none()

    if not package:
        raise HTTPException(status_code=404, detail="패키지를 찾을 수 없습니다.")

    # 실제 삭제 대신 비활성화
    package.is_active = False
    db.commit()

    return {"message": "패키지가 비활성화되었습니다."}

@router.get("/purchases")
def get_package_purchases(
    customer_id: Optional[int] = None,
    is_active: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """패키지 구매 내역 조회"""
    query = select(
        PackagePurchaseModel,
        PackageModel.package_name,
        CustomerModel.name.label('customer_name'),
        CustomerModel.phone.label('customer_phone')
    ).join(
        PackageModel, PackagePurchaseModel.package_id == PackageModel.package_id
    ).join(
        CustomerModel, PackagePurchaseModel.customer_id == CustomerModel.customer_id
    )

    if customer_id:
        query = query.where(PackagePurchaseModel.customer_id == customer_id)

    if is_active:
        query = query.where(
            and_(
                PackagePurchaseModel.remaining_sessions > 0,
                PackagePurchaseModel.expiry_date >= date.today()
            )
        )

    query = query.order_by(PackagePurchaseModel.purchase_date.desc())
    query = query.offset(skip).limit(limit)

    result = db.execute(query)
    rows = result.all()

    purchases = []
    for row in rows:
        purchase = row[0]
        purchases.append({
            "purchase_id": purchase.purchase_id,
            "customer_id": purchase.customer_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "package_id": purchase.package_id,
            "package_name": row.package_name,
            "purchase_date": purchase.purchase_date.isoformat(),
            "expiry_date": purchase.expiry_date.isoformat() if purchase.expiry_date else None,
            "total_sessions": purchase.total_sessions,
            "used_sessions": purchase.used_sessions,
            "remaining_sessions": purchase.remaining_sessions,
            "is_active": purchase.remaining_sessions > 0 and (not purchase.expiry_date or purchase.expiry_date >= date.today())
        })

    return purchases

@router.get("/purchases/stats")
def get_package_stats(
    db: Session = Depends(get_db)
):
    """패키지 구매 통계"""
    # 활성 패키지 구매 수
    active_query = select(func.count(PackagePurchaseModel.purchase_id)).where(
        and_(
            PackagePurchaseModel.remaining_sessions > 0,
            PackagePurchaseModel.expiry_date >= date.today()
        )
    )
    active_result = db.execute(active_query)
    active_count = active_result.scalar()

    # 전체 잔여 세션 수
    remaining_query = select(func.sum(PackagePurchaseModel.remaining_sessions)).where(
        and_(
            PackagePurchaseModel.remaining_sessions > 0,
            PackagePurchaseModel.expiry_date >= date.today()
        )
    )
    remaining_result = db.execute(remaining_query)
    total_remaining = remaining_result.scalar() or 0

    # 이번 달 만료 예정
    expiring_query = select(func.count(PackagePurchaseModel.purchase_id)).where(
        and_(
            PackagePurchaseModel.remaining_sessions > 0,
            PackagePurchaseModel.expiry_date >= date.today(),
            func.extract('month', PackagePurchaseModel.expiry_date) == date.today().month,
            func.extract('year', PackagePurchaseModel.expiry_date) == date.today().year
        )
    )
    expiring_result = db.execute(expiring_query)
    expiring_count = expiring_result.scalar()

    return {
        "active_purchases": active_count,
        "total_remaining_sessions": total_remaining,
        "expiring_this_month": expiring_count
    }

@router.get("/customer/{customer_id}/active")
def get_customer_active_packages(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """고객의 활성 패키지 조회"""
    query = select(
        PackagePurchaseModel,
        PackageModel.package_name
    ).join(
        PackageModel, PackagePurchaseModel.package_id == PackageModel.package_id
    ).where(
        and_(
            PackagePurchaseModel.customer_id == customer_id,
            PackagePurchaseModel.remaining_sessions > 0,
            PackagePurchaseModel.expiry_date >= date.today()
        )
    ).order_by(PackagePurchaseModel.expiry_date)

    result = db.execute(query)
    rows = result.all()

    packages = []
    for row in rows:
        purchase = row[0]
        packages.append({
            "purchase_id": purchase.purchase_id,
            "package_id": purchase.package_id,
            "package_name": row.package_name,
            "purchase_date": purchase.purchase_date.isoformat(),
            "expiry_date": purchase.expiry_date.isoformat() if purchase.expiry_date else None,
            "total_sessions": purchase.total_sessions,
            "used_sessions": purchase.used_sessions,
            "remaining_sessions": purchase.remaining_sessions
        })

    return packages
