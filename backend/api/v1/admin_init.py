"""
관리자 초기화 엔드포인트
프로덕션 환경에서 비밀번호를 초기화하기 위한 임시 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User
from core.auth import get_password_hash
import os

router = APIRouter()

@router.post("/init-accounts")
def initialize_accounts(
    secret_key: str,
    db: Session = Depends(get_db)
):
    """
    비밀번호 초기화 엔드포인트
    보안을 위해 환경 변수의 secret key가 필요합니다.
    """

    # 환경 변수에서 설정한 초기화 키 확인
    init_key = os.getenv("ADMIN_INIT_KEY", "aibio-init-2025")

    if secret_key != init_key:
        raise HTTPException(status_code=403, detail="Invalid secret key")

    results = []

    try:
        # admin@aibio.kr 초기화
        admin_user = db.query(User).filter(User.email == "admin@aibio.kr").first()
        if admin_user:
            admin_user.password_hash = get_password_hash("admin123")
            admin_user.is_active = True
            results.append("✅ admin@aibio.kr 비밀번호 초기화 완료")
        else:
            # 계정 생성
            new_admin = User(
                email="admin@aibio.kr",
                name="관리자",
                password_hash=get_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            db.add(new_admin)
            results.append("✅ admin@aibio.kr 계정 생성 완료")

        # taejun@biocom.kr 초기화
        master_user = db.query(User).filter(User.email == "taejun@biocom.kr").first()
        if master_user:
            master_user.password_hash = get_password_hash("admin1234")
            master_user.is_active = True
            master_user.role = "master"
            results.append("✅ taejun@biocom.kr 비밀번호 초기화 완료")
        else:
            # 계정 생성
            new_master = User(
                email="taejun@biocom.kr",
                name="TaeJun",
                password_hash=get_password_hash("admin1234"),
                role="master",
                is_active=True
            )
            db.add(new_master)
            results.append("✅ taejun@biocom.kr 계정 생성 완료")

        # manager@aibio.kr 초기화
        manager_user = db.query(User).filter(User.email == "manager@aibio.kr").first()
        if manager_user:
            manager_user.password_hash = get_password_hash("manager123")
            manager_user.is_active = True
            manager_user.role = "manager"
            results.append("✅ manager@aibio.kr 비밀번호 초기화 완료")

        db.commit()

        return {
            "success": True,
            "results": results,
            "accounts": [
                {"email": "admin@aibio.kr", "password": "admin123", "role": "admin"},
                {"email": "taejun@biocom.kr", "password": "admin1234", "role": "master"},
                {"email": "manager@aibio.kr", "password": "manager123", "role": "manager"}
            ]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/check-users")
def check_users(db: Session = Depends(get_db)):
    """현재 사용자 목록 확인 (공개 엔드포인트)"""
    users = db.query(User).all()

    return {
        "total_users": len(users),
        "users": [
            {
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_active": user.is_active
            }
            for user in users
        ]
    }
