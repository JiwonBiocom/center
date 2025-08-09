from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, date
import logging

from core.database import get_db
from core.auth import get_current_user
from models import User, Customer
from services.aligo_service import aligo_service, sms_templates
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

class SMSSendRequest(BaseModel):
    """SMS 발송 요청"""
    customer_ids: List[int]
    message: str
    title: Optional[str] = None

class SMSTemplateRequest(BaseModel):
    """템플릿 SMS 발송 요청"""
    customer_ids: List[int]
    template_type: str  # confirmation, reminder, cancelled, completed, birthday, dormant, promotion
    template_data: Optional[Dict] = None

class SMSResponse(BaseModel):
    """SMS 발송 응답"""
    success: bool
    total_count: int
    success_count: int
    error_count: int
    message: Optional[str] = None
    details: Optional[Dict] = None

@router.post("/send", response_model=SMSResponse)
def send_sms(
    request: SMSSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """개별/단체 SMS 발송"""
    
    # 고객 정보 조회
    customers = db.query(Customer).filter(
        Customer.customer_id.in_(request.customer_ids)
    ).all()
    
    if not customers:
        raise HTTPException(
            status_code=404,
            detail="선택한 고객을 찾을 수 없습니다"
        )
    
    # 전화번호가 있는 고객만 필터링
    valid_customers = [c for c in customers if c.phone]
    
    if not valid_customers:
        raise HTTPException(
            status_code=400,
            detail="전화번호가 등록된 고객이 없습니다"
        )
    
    # 단일 발송 또는 대량 발송 결정
    if len(valid_customers) == 1:
        # 단일 발송
        result = aligo_service.send_sms(
            receiver=valid_customers[0].phone,
            message=request.message,
            title=request.title
        )
        
        return SMSResponse(
            success=result["success"],
            total_count=1,
            success_count=1 if result["success"] else 0,
            error_count=0 if result["success"] else 1,
            message=result.get("error_message") if not result["success"] else "발송 완료",
            details=result
        )
    else:
        # 대량 발송
        receivers = [
            {
                "phone": c.phone,
                "message": request.message,
                "name": c.name
            }
            for c in valid_customers
        ]
        
        result = aligo_service.send_mass(receivers)
        
        return SMSResponse(
            success=result["success"],
            total_count=len(valid_customers),
            success_count=result.get("success_cnt", 0),
            error_count=result.get("error_cnt", 0),
            message=result.get("error_message") if not result["success"] else "발송 완료",
            details=result
        )

@router.post("/send-template", response_model=SMSResponse)
def send_template_sms(
    request: SMSTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """템플릿 기반 SMS 발송"""
    
    # 고객 정보 조회
    customers = db.query(Customer).filter(
        Customer.customer_id.in_(request.customer_ids)
    ).all()
    
    if not customers:
        raise HTTPException(
            status_code=404,
            detail="선택한 고객을 찾을 수 없습니다"
        )
    
    # 전화번호가 있는 고객만 필터링
    valid_customers = [c for c in customers if c.phone]
    
    if not valid_customers:
        raise HTTPException(
            status_code=400,
            detail="전화번호가 등록된 고객이 없습니다"
        )
    
    # 템플릿별 메시지 생성
    receivers = []
    for customer in valid_customers:
        message = None
        
        if request.template_type == "birthday":
            message = sms_templates.birthday_greeting(customer.name)
        elif request.template_type == "dormant":
            last_visit = customer.last_visit_date.strftime("%Y-%m-%d") if customer.last_visit_date else "미방문"
            message = sms_templates.dormant_customer_reactivation(customer.name, last_visit)
        elif request.template_type == "promotion" and request.template_data:
            message = sms_templates.promotion(
                customer.name,
                request.template_data.get("title", "특별 혜택"),
                request.template_data.get("content", "")
            )
        
        if message:
            receivers.append({
                "phone": customer.phone,
                "message": message,
                "name": customer.name
            })
    
    if not receivers:
        raise HTTPException(
            status_code=400,
            detail="발송할 메시지가 없습니다"
        )
    
    # 대량 발송
    result = aligo_service.send_mass(receivers)
    
    return SMSResponse(
        success=result["success"],
        total_count=len(receivers),
        success_count=result.get("success_cnt", 0),
        error_count=result.get("error_cnt", 0),
        message=result.get("error_message") if not result["success"] else "템플릿 발송 완료",
        details=result
    )

@router.get("/remain")
def get_sms_remain(
    current_user: User = Depends(get_current_user)
):
    """SMS 잔여건수 조회"""
    try:
        result = aligo_service.get_remain_sms()
        
        if result.get("success"):
            return {
                "sms_count": result.get("sms_count", 0),
                "lms_count": result.get("lms_count", 0),
                "mms_count": result.get("mms_count", 0)
            }
        else:
            # 실패해도 0으로 반환 (모달은 계속 사용 가능)
            logger.warning(f"SMS 잔여건수 조회 실패: {result.get('error')}")
            return {
                "sms_count": 0,
                "lms_count": 0,
                "mms_count": 0
            }
    except Exception as e:
        logger.error(f"SMS 잔여건수 조회 중 오류: {str(e)}")
        # 오류 발생해도 0으로 반환
        return {
            "sms_count": 0,
            "lms_count": 0,
            "mms_count": 0
        }

@router.get("/history")
def get_sms_history(
    page: int = 1,
    page_size: int = 30,
    start_date: Optional[str] = None,
    limit_day: int = 7,
    current_user: User = Depends(get_current_user)
):
    """SMS 발송 이력 조회"""
    result = aligo_service.get_sent_list(
        page=page,
        page_size=page_size,
        start_date=start_date,
        limit_day=limit_day
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "발송 이력 조회 실패")
        )
    
    return {
        "list": result["list"],
        "total_count": result["total_count"],
        "current_page": result["current_page"]
    }