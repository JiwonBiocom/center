from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, select
from datetime import date
from typing import Optional
from core.database import get_db
from models.payment import Payment

router = APIRouter()

@router.get("/performance")
def get_staff_performance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get staff performance metrics"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, end_date.month, 1)  # Current month
    
    # Get payment statistics by staff
    payment_stmt = (
        select(
            Payment.payment_staff,
            func.sum(Payment.amount).label('total_revenue'),
            func.count(Payment.payment_id).label('payment_count'),
            func.count(func.distinct(Payment.customer_id)).label('unique_customers')
        )
        .where(
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
        .group_by(Payment.payment_staff)
        .order_by(desc('total_revenue'))
    )
    
    payment_result = db.execute(payment_stmt)
    staff_stats = payment_result.all()
    
    # Format data
    chart_data = []
    for row in staff_stats:
        chart_data.append({
            "staff": row.payment_staff or "미지정",
            "revenue": float(row.total_revenue) if row.total_revenue else 0,
            "payments": row.payment_count,
            "customers": row.unique_customers
        })
    
    return {
        "data": chart_data,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }