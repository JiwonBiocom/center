from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from models import User, CompanyInfo
from core.auth import get_current_user

router = APIRouter()

@router.get("/company")
def get_company_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """회사 정보 조회"""
    company = db.query(CompanyInfo).first()
    if not company:
        return {
            "company_name": "AIBIO Center",
            "address": "",
            "phone": "",
            "email": "",
            "business_hours": {},
            "holidays": []
        }
    return company

@router.put("/company")
def update_company_info(
    company_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """회사 정보 수정 (관리자 전용)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    company = db.query(CompanyInfo).first()
    if not company:
        company = CompanyInfo(**company_data)
        db.add(company)
    else:
        for key, value in company_data.items():
            if hasattr(company, key):
                setattr(company, key, value)

    db.commit()
    return {"message": "회사 정보가 업데이트되었습니다."}
