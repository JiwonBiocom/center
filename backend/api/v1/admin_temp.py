"""
임시 관리자 엔드포인트 - 서비스 타입 복원용
프로덕션에서 한 번만 실행 후 삭제 예정
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from core.database import get_db
from core.auth import get_current_user
from models.user import User

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

router = APIRouter()

@router.post("/restore-services", response_model=Dict[str, str])
async def restore_services(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """서비스 타입을 복원하는 임시 엔드포인트"""

    # 관리자만 실행 가능
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 실행할 수 있습니다"
        )

    try:
        # 스크립트 실행
        from scripts.restore_correct_services_auto import restore_correct_services
        restore_correct_services()

        return {"status": "success", "message": "서비스 타입이 성공적으로 복원되었습니다"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"복원 중 오류 발생: {str(e)}"
        )
