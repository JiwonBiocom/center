from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import date, timedelta

from core.database import get_db
from models.payment import Payment as PaymentModel
from models.customer import Customer as CustomerModel

router = APIRouter()

@router.get("/summary")
def get_payment_summary(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """결제 통계 요약"""
    query = select(
        func.count(PaymentModel.payment_id).label('total_count'),
        func.sum(PaymentModel.amount).label('total_amount'),
        func.count(func.distinct(PaymentModel.customer_id)).label('unique_customers')
    )
    
    if date_from:
        query = query.where(PaymentModel.payment_date >= date_from)
    if date_to:
        query = query.where(PaymentModel.payment_date <= date_to)
    
    result = db.execute(query)
    summary = result.one()
    
    # 결제 방법별 통계
    method_query = select(
        PaymentModel.payment_method,
        func.count(PaymentModel.payment_id).label('count'),
        func.sum(PaymentModel.amount).label('amount')
    ).group_by(PaymentModel.payment_method)
    
    if date_from:
        method_query = method_query.where(PaymentModel.payment_date >= date_from)
    if date_to:
        method_query = method_query.where(PaymentModel.payment_date <= date_to)
    
    method_result = db.execute(method_query)
    method_stats = method_result.all()
    
    return {
        "total_count": summary.total_count or 0,
        "total_amount": float(summary.total_amount or 0),
        "unique_customers": summary.unique_customers or 0,
        "by_method": [
            {
                "method": stat.payment_method,
                "count": stat.count,
                "amount": float(stat.amount)
            }
            for stat in method_stats
        ]
    }

@router.get("/daily")
def get_daily_revenue(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """일별 매출 통계"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    query = select(
        PaymentModel.payment_date,
        func.count(PaymentModel.payment_id).label('count'),
        func.sum(PaymentModel.amount).label('revenue')
    ).where(
        and_(
            PaymentModel.payment_date >= start_date,
            PaymentModel.payment_date < end_date
        )
    ).group_by(PaymentModel.payment_date).order_by(PaymentModel.payment_date)
    
    result = db.execute(query)
    daily_stats = result.all()
    
    # 전체 날짜에 대한 데이터 생성
    daily_data = {}
    for stat in daily_stats:
        daily_data[stat.payment_date] = {
            "count": stat.count,
            "revenue": float(stat.revenue)
        }
    
    # 빈 날짜 채우기
    current = start_date
    result_data = []
    while current < end_date:
        if current in daily_data:
            result_data.append({
                "date": current.isoformat(),
                "count": daily_data[current]["count"],
                "revenue": daily_data[current]["revenue"]
            })
        else:
            result_data.append({
                "date": current.isoformat(),
                "count": 0,
                "revenue": 0
            })
        current += timedelta(days=1)
    
    return result_data

@router.get("/top-customers")
def get_top_customers(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """매출 상위 고객"""
    query = select(
        PaymentModel.customer_id,
        CustomerModel.name,
        CustomerModel.phone,
        func.count(PaymentModel.payment_id).label('payment_count'),
        func.sum(PaymentModel.amount).label('total_amount'),
        func.max(PaymentModel.payment_date).label('last_payment_date')
    ).join(
        CustomerModel, PaymentModel.customer_id == CustomerModel.customer_id
    ).group_by(
        PaymentModel.customer_id, CustomerModel.name, CustomerModel.phone
    )
    
    if date_from:
        query = query.where(PaymentModel.payment_date >= date_from)
    if date_to:
        query = query.where(PaymentModel.payment_date <= date_to)
    
    query = query.order_by(func.sum(PaymentModel.amount).desc()).limit(limit)
    
    result = db.execute(query)
    customers = result.all()
    
    return [
        {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "phone": customer.phone,
            "payment_count": customer.payment_count,
            "total_amount": float(customer.total_amount),
            "last_payment_date": customer.last_payment_date.isoformat()
        }
        for customer in customers
    ]