from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, select
from datetime import date, timedelta
from typing import Optional
from core.database import get_db
from models.payment import Payment
from models.customer import Customer
from models.service import ServiceUsage
from utils.report_generator import ReportGenerator

router = APIRouter()
report_generator = ReportGenerator()

@router.get("/acquisition")
def get_customer_acquisition(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get customer acquisition trend data"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=180)  # Last 6 months
    
    # Query new customers by month
    stmt = (
        select(
            extract('year', Customer.first_visit_date).label('year'),
            extract('month', Customer.first_visit_date).label('month'),
            func.count(Customer.customer_id).label('new_customers')
        )
        .where(
            (Customer.first_visit_date >= start_date) &
            (Customer.first_visit_date <= end_date)
        )
        .group_by(
            extract('year', Customer.first_visit_date),
            extract('month', Customer.first_visit_date)
        )
        .order_by(
            extract('year', Customer.first_visit_date),
            extract('month', Customer.first_visit_date)
        )
    )
    
    result = db.execute(stmt)
    new_customers = result.all()
    
    # Get total customers over time
    chart_data = []
    cumulative_total = 0
    
    # Get initial count
    initial_count_result = db.execute(
        select(func.count(Customer.customer_id))
        .where(Customer.first_visit_date < start_date)
    )
    cumulative_total = initial_count_result.scalar() or 0
    
    for row in new_customers:
        cumulative_total += row.new_customers
        chart_data.append({
            "month": f"{int(row.year)}-{int(row.month):02d}",
            "new_customers": row.new_customers,
            "total_customers": cumulative_total
        })
    
    return {
        "data": chart_data,
        "summary": {
            "total_new_customers": sum(item["new_customers"] for item in chart_data),
            "current_total": cumulative_total
        }
    }

@router.get("/generate/customer-analysis")
def generate_customer_analysis_pdf(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db)
):
    """Generate customer analysis report PDF"""
    # Default to last 90 days if no dates provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=90)
    
    # Get total customers
    total_customers_result = db.execute(
        select(func.count(Customer.customer_id))
    )
    total_customers = total_customers_result.scalar() or 0
    
    # Get new customers in period
    new_customers_result = db.execute(
        select(func.count(Customer.customer_id))
        .where(
            (Customer.first_visit_date >= start_date) &
            (Customer.first_visit_date <= end_date)
        )
    )
    new_customers = new_customers_result.scalar() or 0
    
    # Get returning customers (had services before the period)
    returning_customers_result = db.execute(
        select(func.count(func.distinct(ServiceUsage.customer_id)))
        .where(
            (ServiceUsage.service_date >= start_date) &
            (ServiceUsage.service_date <= end_date) &
            (ServiceUsage.customer_id.in_(
                select(Customer.customer_id)
                .where(Customer.first_visit_date < start_date)
            ))
        )
    )
    returning_customers = returning_customers_result.scalar() or 0
    
    # Get average visits per customer
    avg_visits_stmt = (
        select(
            func.count(ServiceUsage.usage_id).label('total_visits'),
            func.count(func.distinct(ServiceUsage.customer_id)).label('unique_customers')
        )
        .where(
            (ServiceUsage.service_date >= start_date) &
            (ServiceUsage.service_date <= end_date)
        )
    )
    
    avg_visits_result = db.execute(avg_visits_stmt)
    avg_data = avg_visits_result.one()
    avg_visits = avg_data.total_visits / avg_data.unique_customers if avg_data.unique_customers > 0 else 0
    
    # Get average purchase amount
    avg_purchase_stmt = (
        select(func.avg(Payment.amount))
        .where(
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
    )
    
    avg_purchase_result = db.execute(avg_purchase_stmt)
    avg_purchase_amount = avg_purchase_result.scalar() or 0
    
    # Get region distribution
    region_stmt = (
        select(
            Customer.region,
            func.count(Customer.customer_id).label('count')
        )
        .where(Customer.region.is_not(None))
        .group_by(Customer.region)
        .order_by(desc('count'))
        .limit(10)
    )
    
    region_result = db.execute(region_stmt)
    region_data = region_result.all()
    
    region_distribution = {row.region: row.count for row in region_data}
    
    # Get referral sources
    referral_stmt = (
        select(
            Customer.referral_source,
            func.count(Customer.customer_id).label('count')
        )
        .where(
            (Customer.first_visit_date >= start_date) &
            (Customer.first_visit_date <= end_date) &
            (Customer.referral_source.is_not(None))
        )
        .group_by(Customer.referral_source)
        .order_by(desc('count'))
    )
    
    referral_result = db.execute(referral_stmt)
    referral_data = referral_result.all()
    
    referral_sources = {row.referral_source: row.count for row in referral_data}
    
    # Get top customers
    top_customers_stmt = (
        select(
            Customer.name,
            Customer.customer_id,
            func.count(ServiceUsage.usage_id).label('visits'),
            func.sum(Payment.amount).label('total_amount')
        )
        .join(ServiceUsage, Customer.customer_id == ServiceUsage.customer_id, isouter=True)
        .join(Payment, Customer.customer_id == Payment.customer_id, isouter=True)
        .where(
            (ServiceUsage.service_date >= start_date) &
            (ServiceUsage.service_date <= end_date) &
            (Payment.payment_date >= start_date) &
            (Payment.payment_date <= end_date)
        )
        .group_by(Customer.customer_id, Customer.name)
        .order_by(desc('total_amount'))
        .limit(10)
    )
    
    top_result = db.execute(top_customers_stmt)
    top_data = top_result.all()
    
    top_customers = [
        {
            'name': row.name,
            'visits': row.visits,
            'total_amount': float(row.total_amount) if row.total_amount else 0
        }
        for row in top_data
    ]
    
    # Prepare report data
    report_data = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'total_customers': total_customers,
        'new_customers': new_customers,
        'returning_customers': returning_customers,
        'avg_visits': avg_visits,
        'avg_purchase_amount': float(avg_purchase_amount),
        'region_distribution': region_distribution,
        'referral_sources': referral_sources,
        'top_customers': top_customers
    }
    
    # Generate PDF
    pdf_data = report_generator.generate_customer_analysis_report(report_data)
    
    return Response(
        content=pdf_data,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename=customer_analysis_{start_date}_{end_date}.pdf'
        }
    )