from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, timedelta
from typing import Optional
import csv
import io
from core.database import get_db
from models.payment import Payment
from models.customer import Customer

router = APIRouter()

@router.get("/revenue")
def export_revenue_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Export revenue report as CSV"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=365)
    
    # Get detailed revenue data
    stmt = (
        select(Payment)
        .where(
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
        .order_by(Payment.payment_date.desc())
    )
    
    result = db.execute(stmt)
    payments = result.scalars().all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['결제일', '고객명', '결제금액', '결제방법', '담당직원', '구매유형'])
    
    # Write data
    for payment in payments:
        # Get customer name
        customer_result = db.execute(
            select(Customer.name)
            .where(Customer.customer_id == payment.customer_id)
        )
        customer_name = customer_result.scalar() or "Unknown"
        
        writer.writerow([
            payment.payment_date.strftime('%Y-%m-%d'),
            customer_name,
            payment.amount,
            payment.payment_method,
            payment.payment_staff or '',
            payment.purchase_type or ''
        ])
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=revenue_report_{start_date}_{end_date}.csv"
        }
    )