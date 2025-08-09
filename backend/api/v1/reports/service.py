from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, select
from datetime import date, timedelta
from typing import Optional
from core.database import get_db
from models.service import ServiceUsage, ServiceType

router = APIRouter()

@router.get("/usage")
def get_service_usage_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get service usage statistics by type"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=90)  # Last 3 months
    
    # Get service usage counts by type
    stmt = (
        select(
            ServiceType.service_name,
            func.count(ServiceUsage.usage_id).label('usage_count'),
            func.count(func.distinct(ServiceUsage.customer_id)).label('unique_customers')
        )
        .join(ServiceUsage, ServiceType.service_type_id == ServiceUsage.service_type_id)
        .where(
            (ServiceUsage.service_date >= start_date) &
            (ServiceUsage.service_date <= end_date)
        )
        .group_by(ServiceType.service_name)
        .order_by(desc('usage_count'))
    )
    
    result = db.execute(stmt)
    service_stats = result.all()
    
    # Format data
    chart_data = []
    for row in service_stats:
        chart_data.append({
            "service": row.service_name,
            "usage_count": row.usage_count,
            "unique_customers": row.unique_customers
        })
    
    return {
        "data": chart_data,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }

@router.get("/trends")
def get_service_trends(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get service usage trends over time"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=180)
    
    # Query service usage by month and type
    stmt = (
        select(
            extract('year', ServiceUsage.service_date).label('year'),
            extract('month', ServiceUsage.service_date).label('month'),
            ServiceType.service_name,
            func.count(ServiceUsage.usage_id).label('count')
        )
        .join(ServiceType, ServiceUsage.service_type_id == ServiceType.service_type_id)
        .where(
            (ServiceUsage.service_date >= start_date) &
            (ServiceUsage.service_date <= end_date)
        )
        .group_by(
            extract('year', ServiceUsage.service_date),
            extract('month', ServiceUsage.service_date),
            ServiceType.service_name
        )
        .order_by(
            extract('year', ServiceUsage.service_date),
            extract('month', ServiceUsage.service_date)
        )
    )
    
    result = db.execute(stmt)
    service_trends = result.all()
    
    # Organize data by month
    trends_by_month = {}
    for row in service_trends:
        month_key = f"{int(row.year)}-{int(row.month):02d}"
        if month_key not in trends_by_month:
            trends_by_month[month_key] = {"month": month_key}
        trends_by_month[month_key][row.service_name] = row.count
    
    # Convert to list
    chart_data = list(trends_by_month.values())
    
    return {
        "data": chart_data,
        "services": list(set(row.service_name for row in service_trends))
    }