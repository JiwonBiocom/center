from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from models import User
from core.auth import get_current_user

router = APIRouter()

@router.post("/create")
def create_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """데이터베이스 백업 생성 (관리자 전용)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    # TODO: 실제 백업 로직 구현
    # 여기서는 시뮬레이션만
    backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    return {
        "message": "백업이 생성되었습니다.",
        "filename": backup_filename,
        "size": "12.5 MB",
        "created_at": datetime.now()
    }

@router.get("/list")
def list_backups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """백업 목록 조회 (관리자 전용)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    # TODO: 실제 백업 파일 목록 조회
    # 여기서는 시뮬레이션
    backups = [
        {
            "filename": "backup_20250105_120000.sql",
            "size": "12.5 MB",
            "created_at": "2025-01-05T12:00:00"
        },
        {
            "filename": "backup_20250104_180000.sql",
            "size": "11.8 MB",
            "created_at": "2025-01-04T18:00:00"
        }
    ]

    return backups
