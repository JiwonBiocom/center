from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, select
from datetime import date, timedelta
from typing import Optional
from core.database import get_db
from models.payment import Payment
from models.service import ServiceUsage, ServiceType
from utils.report_generator import ReportGenerator

router = APIRouter()
report_generator = ReportGenerator()

@router.get("/monthly")
def get_monthly_revenue(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db)
):
    """Get monthly revenue data for charts"""
    # Default to last 12 months if no dates provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=365)
    
    # Query monthly revenue
    stmt = (
        select(
            extract('year', Payment.payment_date).label('year'),
            extract('month', Payment.payment_date).label('month'),
            func.sum(Payment.amount).label('total_revenue'),
            func.count(Payment.payment_id).label('transaction_count')
        )
        .where(
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
        .group_by(
            extract('year', Payment.payment_date),
            extract('month', Payment.payment_date)
        )
        .order_by(
            extract('year', Payment.payment_date),
            extract('month', Payment.payment_date)
        )
    )
    
    result = db.execute(stmt)
    monthly_revenue = result.all()
    
    # Format the data for charts
    chart_data = []
    for row in monthly_revenue:
        chart_data.append({
            "month": f"{int(row.year)}-{int(row.month):02d}",
            "revenue": float(row.total_revenue) if row.total_revenue else 0,
            "transactions": row.transaction_count
        })
    
    return {
        "data": chart_data,
        "summary": {
            "total_revenue": sum(item["revenue"] for item in chart_data),
            "total_transactions": sum(item["transactions"] for item in chart_data),
            "average_transaction": sum(item["revenue"] for item in chart_data) / max(sum(item["transactions"] for item in chart_data), 1)
        }
    }

@router.get("/generate/monthly-revenue")
def generate_monthly_revenue_pdf(
    year: int = Query(..., description="Year for the report"),
    month: int = Query(..., description="Month for the report (1-12)"),
    db: Session = Depends(get_db)
):
    """Generate monthly revenue report PDF"""
    # Calculate date range
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get current month revenue
    current_revenue_result = db.execute(
        select(func.sum(Payment.amount))
        .where(
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
    )
    total_revenue = current_revenue_result.scalar() or 0
    
    # Get transaction count
    transaction_count_result = db.execute(
        select(func.count(Payment.payment_id))
        .where(
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
    )
    total_transactions = transaction_count_result.scalar() or 0
    
    # Calculate daily average
    days_in_month = (end_date - start_date).days + 1
    daily_average = total_revenue / days_in_month if days_in_month > 0 else 0
    
    # Get previous month data for comparison
    prev_month_start = date(year, month - 1, 1) if month > 1 else date(year - 1, 12, 1)
    prev_month_end = start_date - timedelta(days=1)
    
    prev_revenue_result = db.execute(
        select(func.sum(Payment.amount))
        .where(
            (Payment.payment_date >= prev_month_start) &
            (Payment.payment_date <= prev_month_end)
        )
    )
    prev_month_revenue = prev_revenue_result.scalar() or 0
    
    # Calculate month-over-month growth
    mom_growth = ((total_revenue - prev_month_revenue) / prev_month_revenue * 100) if prev_month_revenue > 0 else 0
    
    # Get year-over-year data
    yoy_start = date(year - 1, month, 1)
    yoy_end = date(year - 1, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 1, 1) - timedelta(days=1)
    
    yoy_revenue_result = db.execute(
        select(func.sum(Payment.amount))
        .where(
            (Payment.payment_date >= yoy_start) &
            (Payment.payment_date <= yoy_end)
        )
    )
    yoy_revenue = yoy_revenue_result.scalar() or 0
    
    # Calculate year-over-year growth
    yoy_growth = ((total_revenue - yoy_revenue) / yoy_revenue * 100) if yoy_revenue > 0 else 0
    
    # Get daily revenue data
    daily_revenue_stmt = (
        select(
            extract('day', Payment.payment_date).label('day'),
            func.sum(Payment.amount).label('revenue')
        )
        .where(
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
        .group_by(extract('day', Payment.payment_date))
        .order_by(extract('day', Payment.payment_date))
    )
    
    daily_result = db.execute(daily_revenue_stmt)
    daily_data = daily_result.all()
    
    daily_revenue = {f"{int(row.day)}일": float(row.revenue) for row in daily_data}
    
    # Get service revenue breakdown
    service_usage_stmt = (
        select(
            ServiceType.service_name,
            func.count(ServiceUsage.usage_id).label('usage_count')
        )
        .join(ServiceType, ServiceUsage.service_type_id == ServiceType.service_type_id)
        .where(
            (ServiceUsage.service_date >= start_date) &
            (ServiceUsage.service_date <= end_date)
        )
        .group_by(ServiceType.service_name)
    )
    
    service_result = db.execute(service_usage_stmt)
    service_data = service_result.all()
    
    # Estimate revenue distribution based on service usage
    total_usage = sum(row.usage_count for row in service_data)
    service_revenue = {}
    if total_usage > 0 and total_revenue > 0:
        for row in service_data:
            service_revenue[row.service_name] = float(total_revenue * row.usage_count / total_usage)
    
    # Get payment method stats
    payment_method_stmt = (
        select(
            Payment.payment_method,
            func.count(Payment.payment_id).label('count'),
            func.sum(Payment.amount).label('amount')
        )
        .where(
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
        .group_by(Payment.payment_method)
    )
    
    method_result = db.execute(payment_method_stmt)
    method_data = method_result.all()
    
    payment_methods = {}
    for row in method_data:
        payment_methods[row.payment_method] = {
            'count': row.count,
            'amount': float(row.amount),
            'percentage': float(row.amount) / float(total_revenue) * 100 if total_revenue > 0 else 0
        }
    
    # Prepare report data
    report_data = {
        'year': year,
        'month': month,
        'total_revenue': float(total_revenue),
        'total_transactions': total_transactions,
        'daily_average': float(daily_average),
        'month_over_month_growth': mom_growth,
        'year_over_year_growth': yoy_growth,
        'daily_revenue': daily_revenue,
        'service_revenue': service_revenue,
        'payment_methods': payment_methods
    }
    
    # Generate PDF
    pdf_data = report_generator.generate_monthly_revenue_report(report_data)
    
    return Response(
        content=pdf_data,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename=monthly_revenue_{year}_{month:02d}.pdf'
        }
    )