from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from core.database import get_db
from models.payment import Payment as PaymentModel
from models.customer import Customer as CustomerModel
from utils.receipt import generate_receipt_html, generate_simple_receipt

router = APIRouter()

@router.get("/{payment_id}/receipt")
def get_payment_receipt(
    payment_id: int,
    format: str = Query("html", regex="^(html|text)$"),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """영수증 조회/출력"""
    # 결제 정보 조회
    query = select(
        PaymentModel,
        CustomerModel
    ).join(
        CustomerModel, PaymentModel.customer_id == CustomerModel.customer_id
    ).where(PaymentModel.payment_id == payment_id)
    
    result = db.execute(query)
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(status_code=404, detail="결제 내역을 찾을 수 없습니다.")
    
    payment, customer = row
    
    # 결제 데이터 준비
    payment_data = {
        "payment_id": payment.payment_id,
        "payment_date": payment.payment_date,
        "amount": float(payment.amount),
        "payment_method": payment.payment_method,
        "card_holder_name": payment.card_holder_name,
        "approval_number": payment.approval_number,
        "payment_staff": payment.payment_staff,
        "purchase_type": payment.purchase_type,
        "purchase_order": payment.purchase_order
    }
    
    customer_data = {
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email
    }
    
    if format == "html":
        # HTML 영수증 반환
        html_content = generate_receipt_html(payment_data, customer_data)
        return HTMLResponse(content=html_content)
    else:
        # 텍스트 영수증 반환
        text_content = generate_simple_receipt(payment_data, customer_data)
        return Response(content=text_content, media_type="text/plain; charset=utf-8")