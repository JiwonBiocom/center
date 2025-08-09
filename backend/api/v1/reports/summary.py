from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from datetime import date, timedelta
from core.database import get_db
from models.payment import Payment
from models.customer import Customer
from models.service import ServiceUsage

router = APIRouter()

@router.get("/summary")
def get_summary_report(
    db: Session = Depends(get_db)
):
    """Get summary statistics for dashboard"""
    today = date.today()
    month_start = date(today.year, today.month, 1)
    year_start = date(today.year, 1, 1)
    
    # Current month revenue
    month_revenue_result = db.execute(
        select(func.sum(Payment.amount))
        .where(Payment.payment_date >= month_start)
    )
    month_revenue = month_revenue_result.scalar() or 0
    
    # Year to date revenue
    ytd_revenue_result = db.execute(
        select(func.sum(Payment.amount))
        .where(Payment.payment_date >= year_start)
    )
    ytd_revenue = ytd_revenue_result.scalar() or 0
    
    # Total customers
    total_customers_result = db.execute(
        select(func.count(Customer.customer_id))
    )
    total_customers = total_customers_result.scalar() or 0
    
    # New customers this month
    new_customers_result = db.execute(
        select(func.count(Customer.customer_id))
        .where(Customer.first_visit_date >= month_start)
    )
    new_customers_month = new_customers_result.scalar() or 0
    
    # Active customers (visited in last 30 days)
    active_date = today - timedelta(days=30)
    active_customers_result = db.execute(
        select(func.count(func.distinct(ServiceUsage.customer_id)))
        .where(ServiceUsage.service_date >= active_date)
    )
    active_customers = active_customers_result.scalar() or 0
    
    # Total services this month
    services_month_result = db.execute(
        select(func.count(ServiceUsage.usage_id))
        .where(ServiceUsage.service_date >= month_start)
    )
    services_month = services_month_result.scalar() or 0
    
    return {
        "monthly_revenue": float(month_revenue),
        "ytd_revenue": float(ytd_revenue),
        "total_customers": total_customers,
        "new_customers_month": new_customers_month,
        "active_customers": active_customers,
        "services_month": services_month
    }