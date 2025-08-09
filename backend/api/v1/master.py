from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from core.database import get_db
from core.auth import check_permission, get_password_hash
from models.user import User
from models.customer import Customer
from models.service import ServiceUsage
from models.payment import Payment
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class PasswordResetRequest(BaseModel):
    user_id: int
    new_password: str

class UserDeleteRequest(BaseModel):
    user_ids: List[int]

class UserResponse(BaseModel):
    user_id: int
    email: str
    name: str
    role: str
    is_active: bool

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("master"))
):
    """모든 사용자 목록 조회 (마스터 권한 필요)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/reset-password")
async def reset_user_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("master"))
):
    """사용자 비밀번호 초기화 (마스터 권한 필요)"""
    # 대상 사용자 확인
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    # 자기 자신의 비밀번호는 변경 불가
    if user.user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자신의 비밀번호는 이 방법으로 변경할 수 없습니다"
        )

    # 비밀번호 업데이트
    user.password_hash = get_password_hash(request.new_password)
    db.commit()

    logger.info(f"마스터 {current_user.email}가 사용자 {user.email}의 비밀번호를 초기화했습니다")

    return {"message": f"사용자 {user.email}의 비밀번호가 초기화되었습니다"}

@router.delete("/users")
async def delete_users(
    request: UserDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("master"))
):
    """사용자 삭제 (마스터 권한 필요)"""
    # 자기 자신은 삭제 불가
    if current_user.user_id in request.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신은 삭제할 수 없습니다"
        )

    # 삭제할 사용자들 확인
    users_to_delete = db.query(User).filter(User.user_id.in_(request.user_ids)).all()

    if not users_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제할 사용자를 찾을 수 없습니다"
        )

    # 다른 마스터 계정이 있는지 확인
    master_count = db.query(User).filter(User.role == "master", User.is_active == True).count()
    masters_to_delete = [u for u in users_to_delete if u.role == "master"]

    if master_count - len(masters_to_delete) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 1개의 마스터 계정은 유지되어야 합니다"
        )

    # 사용자 삭제 (실제로는 비활성화)
    deleted_emails = []
    for user in users_to_delete:
        user.is_active = False
        deleted_emails.append(user.email)

    db.commit()

    logger.info(f"마스터 {current_user.email}가 사용자들을 삭제했습니다: {', '.join(deleted_emails)}")

    return {
        "message": f"{len(users_to_delete)}명의 사용자가 삭제되었습니다",
        "deleted_users": deleted_emails
    }

@router.get("/system-stats")
async def get_system_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("master"))
):
    """시스템 전체 통계 (마스터 권한 필요)"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_customers = db.query(Customer).count()
    total_services = db.query(ServiceUsage).count()
    total_payments = db.query(Payment).count()

    # 역할별 사용자 수
    role_counts = {}
    for role in ["master", "admin", "manager", "staff"]:
        count = db.query(User).filter(User.role == role, User.is_active == True).count()
        role_counts[role] = count

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "by_role": role_counts
        },
        "customers": {
            "total": total_customers
        },
        "services": {
            "total": total_services
        },
        "payments": {
            "total": total_payments
        }
    }

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: str = Query(..., description="새로운 권한 역할"),  # query parameter 지원
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("master"))
):
    """사용자 권한 변경 (마스터 권한 필요)"""
    # 유효한 역할인지 확인
    valid_roles = ["staff", "manager", "admin", "master"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 역할입니다. 가능한 역할: {', '.join(valid_roles)}"
        )

    # 대상 사용자 확인
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    # 마스터 권한 변경 시 주의사항
    if user.role == "master" and new_role != "master":
        # 다른 마스터가 있는지 확인
        master_count = db.query(User).filter(
            User.role == "master",
            User.is_active == True,
            User.user_id != user_id
        ).count()

        if master_count < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="최소 1개의 마스터 계정은 유지되어야 합니다"
            )

    old_role = user.role
    user.role = new_role
    db.commit()

    logger.info(f"마스터 {current_user.email}가 사용자 {user.email}의 권한을 {old_role}에서 {new_role}로 변경했습니다")

    return {
        "message": f"사용자 {user.email}의 권한이 {old_role}에서 {new_role}로 변경되었습니다"
    }

@router.get("/system/overview")
async def get_system_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("master"))
):
    """시스템 전체 개요 (마스터 권한 필요)"""
    try:
        # 사용자 통계
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        user_by_role = {}
        for role in ["master", "admin", "manager", "staff"]:
            count = db.query(User).filter(User.role == role, User.is_active == True).count()
            user_by_role[role] = count

        # 고객 통계
        total_customers = db.query(Customer).count()
        active_customers = db.query(Customer).filter(Customer.status == 'active').count()

        # 서비스 이용 통계
        total_services = db.query(ServiceUsage).count()
        from datetime import datetime, timedelta
        today = datetime.now().date()
        month_start = today.replace(day=1)
        services_this_month = db.query(ServiceUsage).filter(
            ServiceUsage.service_date >= month_start
        ).count()

        # 결제 통계
        from sqlalchemy import func
        total_revenue = db.query(func.sum(Payment.amount)).scalar() or 0
        revenue_this_month = db.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= month_start
        ).scalar() or 0

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "by_role": user_by_role
            },
            "customers": {
                "total": total_customers,
                "active": active_customers
            },
            "services": {
                "total": total_services,
                "this_month": services_this_month
            },
            "revenue": {
                "total": float(total_revenue),
                "this_month": float(revenue_this_month)
            },
            "system": {
                "database": "PostgreSQL",
                "version": "1.0.0",
                "updated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Error getting system overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="시스템 개요 조회 중 오류가 발생했습니다"
        )
