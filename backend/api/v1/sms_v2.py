from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging

from core.database import get_db
from core.auth import get_current_user
from models import User, Customer
from models.customer_extended import MarketingLead
from services.aligo_service import aligo_service, sms_templates
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

class SMSSendRequest(BaseModel):
    """SMS 발송 요청"""
    customer_ids: List[int]
    message: str
    title: Optional[str] = None

class LeadSMSSendRequest(BaseModel):
    """유입고객 SMS 발송 요청"""
    lead_ids: List[int]
    message: str
    title: Optional[str] = None

class LeadSMSTemplateRequest(BaseModel):
    """유입고객 SMS 템플릿 발송 요청"""
    lead_ids: List[int]
    template_type: str
    template_data: Optional[Dict] = None

class SMSTemplateRequest(BaseModel):
    """고객 SMS 템플릿 발송 요청"""
    customer_ids: List[int]
    template_type: str  # birthday, dormant, promotion 등
    template_data: Optional[Dict] = None

@router.get("/remain")
@router.get("/remain/")  # trailing slash 버전도 지원
async def get_sms_remain(current_user: User = Depends(get_current_user)):
    """SMS 잔여건수 조회"""
    # 하드코딩된 값 반환 (테스트용)
    return {
        "sms_count": 117231,
        "lms_count": 39389,
        "mms_count": 16412
    }

@router.post("/send")
async def send_sms(
    request: SMSSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """SMS 발송"""
    # 고객 정보 조회
    customers = db.query(Customer).filter(
        Customer.customer_id.in_(request.customer_ids)
    ).all()

    if not customers:
        return {"success": False, "message": "고객을 찾을 수 없습니다"}

    # 전화번호가 있는 고객만 필터링
    valid_customers = [c for c in customers if c.phone]

    if not valid_customers:
        return {"success": False, "message": "전화번호가 등록된 고객이 없습니다"}

    # 실제 발송 (알리고 서비스 사용)
    if len(valid_customers) == 1:
        result = aligo_service.send_sms(
            receiver=valid_customers[0].phone,
            message=request.message,
            title=request.title
        )
    else:
        receivers = [
            {
                "phone": c.phone,
                "message": request.message,
                "name": c.name
            }
            for c in valid_customers
        ]
        result = aligo_service.send_mass(receivers)

    return {
        "success": result.get("success", False),
        "total_count": len(valid_customers),
        "success_count": result.get("success_cnt", 1 if result.get("success") else 0),
        "error_count": result.get("error_cnt", 0),
        "message": result.get("error_message", "발송 완료" if result.get("success") else "발송 실패")
    }

@router.post("/send-template")
async def send_template_sms(
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
        return {"success": False, "message": "고객을 찾을 수 없습니다"}

    # 전화번호가 있는 고객만 필터링
    valid_customers = [c for c in customers if c.phone]

    if not valid_customers:
        return {"success": False, "message": "전화번호가 등록된 고객이 없습니다"}

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
        else:
            # 기본 메시지
            message = f"[AIBIO 센터] {customer.name}님, 안녕하세요. AIBIO 센터입니다."

        if message:
            receivers.append({
                "phone": customer.phone,
                "message": message,
                "name": customer.name
            })

    # 실제 발송
    if len(receivers) == 1:
        result = aligo_service.send_sms(
            receiver=receivers[0]["phone"],
            message=receivers[0]["message"],
            title="[AIBIO 센터]"
        )
    else:
        result = aligo_service.send_mass(receivers)

    return {
        "success": result.get("success", False),
        "total_count": len(receivers),
        "success_count": result.get("success_cnt", 1 if result.get("success") else 0),
        "error_count": result.get("error_cnt", 0),
        "message": result.get("error_message", "발송 완료" if result.get("success") else "발송 실패"),
        "template_type": request.template_type
    }

@router.post("/send-leads")
async def send_sms_to_leads(
    request: LeadSMSSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객에게 SMS 발송"""
    # 유입고객 정보 조회
    leads = db.query(MarketingLead).filter(
        MarketingLead.lead_id.in_(request.lead_ids)
    ).all()

    if not leads:
        return {"success": False, "message": "유입고객을 찾을 수 없습니다"}

    # 전화번호가 있는 유입고객만 필터링
    valid_leads = [l for l in leads if l.phone]

    if not valid_leads:
        return {"success": False, "message": "전화번호가 등록된 유입고객이 없습니다"}

    # 실제 발송 (알리고 서비스 사용)
    if len(valid_leads) == 1:
        result = aligo_service.send_sms(
            receiver=valid_leads[0].phone,
            message=request.message,
            title=request.title or "[AIBIO 센터]"
        )
    else:
        receivers = [
            {
                "phone": l.phone,
                "message": request.message,
                "name": l.name
            }
            for l in valid_leads
        ]
        result = aligo_service.send_mass(receivers)

    return {
        "success": result.get("success", False),
        "total_count": len(valid_leads),
        "success_count": result.get("success_cnt", 1 if result.get("success") else 0),
        "error_count": result.get("error_cnt", 0),
        "message": result.get("error_message", "발송 완료" if result.get("success") else "발송 실패")
    }

@router.post("/send-leads-template")
async def send_sms_template_to_leads(
    request: LeadSMSTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객에게 템플릿 SMS 발송"""
    # 유입고객 정보 조회
    leads = db.query(MarketingLead).filter(
        MarketingLead.lead_id.in_(request.lead_ids)
    ).all()

    if not leads:
        return {"success": False, "message": "유입고객을 찾을 수 없습니다"}

    # 전화번호가 있는 유입고객만 필터링
    valid_leads = [l for l in leads if l.phone]

    if not valid_leads:
        return {"success": False, "message": "전화번호가 등록된 유입고객이 없습니다"}

    # 템플릿에 따른 메시지 생성
    lead_sms_templates = {
        "initial_contact": "[AIBIO 센터] 안녕하세요!\n{name}님, AIBIO 바이오해킹 센터입니다.\n\n문의해 주셔서 감사합니다. \n개인 맞춤 건강관리 프로그램에 대해 \n자세히 상담드리겠습니다.\n\n상담 예약: 02-2039-2783\n센터 위치: 강남구 테헤란로",
        "visit_invitation": "[AIBIO 센터]\n{name}님, 전화 상담 감사했습니다.\n\n더 정확한 검사와 상담을 위해\n센터 방문을 추천드립니다.\n\n✓ 정밀 체성분 분석\n✓ 1:1 맞춤 상담\n✓ 시설 둘러보기\n\n예약: 02-2039-2783",
        "follow_up": "[AIBIO 센터]\n{name}님, 안녕하세요.\n\n지난 상담 내용 검토해보셨나요?\n추가 궁금한 점이 있으시면\n언제든 연락주세요.\n\n무료 체험 프로그램도 \n준비되어 있습니다.\n\n문의: 02-2039-2783",
        "promotion": "[AIBIO 센터] {title}\n{name}님께 특별 혜택 안내\n\n{content}\n\n자세한 내용과 예약은\n02-2039-2783로 연락주세요."
    }

    if request.template_type not in lead_sms_templates:
        return {"success": False, "message": "지원하지 않는 템플릿 유형입니다"}

    template = lead_sms_templates[request.template_type]

    # 개별 메시지 생성 및 발송
    receivers = []
    for lead in valid_leads:
        if request.template_type == "promotion":
            message = template.format(
                name=lead.name,
                title=request.template_data.get("title", "특별 혜택"),
                content=request.template_data.get("content", "신규 고객 할인 혜택을 확인해보세요.")
            )
        else:
            message = template.format(name=lead.name)

        receivers.append({
            "phone": lead.phone,
            "message": message,
            "name": lead.name
        })

    # 대량 발송
    if len(receivers) == 1:
        result = aligo_service.send_sms(
            receiver=receivers[0]["phone"],
            message=receivers[0]["message"],
            title="[AIBIO 센터]"
        )
    else:
        result = aligo_service.send_mass(receivers)

    return {
        "success": result.get("success", False),
        "total_count": len(valid_leads),
        "success_count": result.get("success_cnt", 1 if result.get("success") else 0),
        "error_count": result.get("error_cnt", 0),
        "message": result.get("error_message", "발송 완료" if result.get("success") else "발송 실패"),
        "template_type": request.template_type
    }
