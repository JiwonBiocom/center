from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from core.database import get_db
from models import User
from models.reservation import KakaoTemplate
from core.auth import get_current_user, get_current_active_user
from core.config import settings

router = APIRouter()

@router.get("/keys")
def get_kakao_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """카카오 API 키 조회 (Admin 키는 마스킹)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    return {
        "rest_api_key": settings.KAKAO_REST_API_KEY[:10] + "*" * (len(settings.KAKAO_REST_API_KEY) - 10) if settings.KAKAO_REST_API_KEY else "",
        "admin_key": settings.KAKAO_ADMIN_KEY[:10] + "*" * (len(settings.KAKAO_ADMIN_KEY) - 10) if settings.KAKAO_ADMIN_KEY else "",
        "sender_key": settings.KAKAO_SENDER_KEY
    }

@router.put("/keys")
def update_kakao_keys(
    keys: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """카카오 API 키 업데이트"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    # 실제 환경에서는 환경변수나 설정 파일에 저장
    # 여기서는 메모리에만 저장 (재시작 시 초기화됨)
    if 'rest_api_key' in keys and not keys['rest_api_key'].endswith('*'):
        settings.KAKAO_REST_API_KEY = keys['rest_api_key']
    if 'admin_key' in keys and not keys['admin_key'].endswith('*'):
        settings.KAKAO_ADMIN_KEY = keys['admin_key']
    if 'sender_key' in keys:
        settings.KAKAO_SENDER_KEY = keys['sender_key']

    return {"message": "API 키가 업데이트되었습니다"}

@router.get("/templates")
def get_kakao_templates(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """카카오 알림톡 템플릿 목록 조회"""
    stmt = select(KakaoTemplate).order_by(KakaoTemplate.created_at.desc())
    result = db.execute(stmt)
    return result.scalars().all()

@router.put("/templates/{template_id}")
def update_kakao_template(
    template_id: int,
    update_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """카카오 알림톡 템플릿 업데이트"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    stmt = select(KakaoTemplate).where(KakaoTemplate.template_id == template_id)
    result = db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    for key, value in update_data.items():
        if hasattr(template, key):
            setattr(template, key, value)

    db.commit()
    return {"message": "템플릿이 업데이트되었습니다"}

@router.post("/test")
def test_kakao_message(
    test_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """카카오톡 테스트 메시지 발송"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    # 여기에 실제 카카오톡 발송 로직 구현
    # from services.kakao_service import KakaoService
    # kakao = KakaoService()
    # result = kakao.send_alimtalk(test_data['phone'], test_data['template_code'], {})

    return {"message": "테스트 메시지가 발송되었습니다"}
