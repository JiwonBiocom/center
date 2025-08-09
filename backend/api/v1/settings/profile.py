from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from models import User
from core.auth import get_current_user, verify_password, get_password_hash
from schemas.user import UserUpdate, PasswordChange

router = APIRouter()

@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user)
):
    """현재 사용자 프로필 조회"""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

@router.put("/profile")
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """프로필 정보 수정"""
    # 이메일 중복 확인
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일입니다."
            )

    # 업데이트
    if user_update.name:
        current_user.name = user_update.name
    if user_update.email:
        current_user.email = user_update.email

    db.commit()
    db.refresh(current_user)

    return {
        "message": "프로필이 성공적으로 업데이트되었습니다.",
        "user": {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role
        }
    }

@router.post("/password/change")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """비밀번호 변경"""
    # 현재 비밀번호 확인
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다."
        )

    # 새 비밀번호 설정
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}
