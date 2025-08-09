from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, extract
from datetime import date, datetime, timedelta

from core.database import get_db
from models import Customer, Payment, PackagePurchase, ServiceUsage, ServiceType
from models.lead_management import LeadConsultationHistory
from core.auth import get_current_user

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """대시보드 통계 조회 - 최적화 버전"""
    today = date.today()
    month_start = date(today.year, today.month, 1)
    thirty_days_ago = today - timedelta(days=30)
    
    # 🚀 최적화: 여러 쿼리를 3개로 통합
    
    # 1. 고객 및 결제 통계 (단일 쿼리)
    from sqlalchemy import case
    
    stats_query = db.query(
        func.count(func.distinct(Customer.customer_id)).label('total_customers'),
        func.sum(
            case(
                (Payment.payment_date == today, Payment.amount),
                else_=0
            )
        ).label('today_revenue'),
        func.sum(
            case(
                (Payment.payment_date >= month_start, Payment.amount),
                else_=0
            )
        ).label('monthly_revenue'),
        func.sum(
            case(
                (Payment.payment_date >= thirty_days_ago, Payment.amount),
                else_=0
            )
        ).label('last_30_days_revenue'),
        func.count(
            func.distinct(
                case(
                    (Customer.first_visit_date >= month_start, Customer.customer_id),
                    else_=None
                )
            )
        ).label('new_customers')
    ).select_from(Customer).outerjoin(Payment, Customer.customer_id == Payment.customer_id)
    
    result = stats_query.first()
    
    # 2. 활성 패키지 (별도 테이블)
    active_packages = db.query(func.count(PackagePurchase.purchase_id)).filter(
        and_(
            PackagePurchase.remaining_sessions > 0,
            PackagePurchase.expiry_date >= today
        )
    ).scalar() or 0
    
    # 3. 오늘 방문 (별도 테이블)
    today_visits = db.query(func.count(func.distinct(ServiceUsage.customer_id))).filter(
        ServiceUsage.service_date == today
    ).scalar() or 0
    
    return {
        "total_customers": result.total_customers or 0,
        "today_revenue": float(result.today_revenue or 0),
        "monthly_revenue": float(result.monthly_revenue or 0),
        "last_30_days_revenue": float(result.last_30_days_revenue or 0),
        "active_packages": active_packages,
        "today_visits": today_visits,
        "new_customers": result.new_customers or 0
    }

@router.get("/revenue-trend")
def get_revenue_trend(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """매출 추이 조회"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    query = db.query(
        Payment.payment_date,
        func.sum(Payment.amount).label('daily_revenue')
    ).filter(
        Payment.payment_date.between(start_date, end_date)
    ).group_by(
        Payment.payment_date
    ).order_by(
        Payment.payment_date
    )
    
    data = query.all()
    
    # 날짜별 데이터 생성 (데이터가 없는 날은 0으로)
    date_revenue_map = {row[0]: float(row[1]) for row in data}
    trend = []
    
    current_date = start_date
    while current_date <= end_date:
        trend.append({
            "date": current_date.isoformat(),
            "revenue": date_revenue_map.get(current_date, 0)
        })
        current_date += timedelta(days=1)
    
    return trend

@router.get("/service-usage-stats")
def get_service_usage_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """서비스별 이용 통계"""
    # 최근 30일 서비스별 이용 횟수
    thirty_days_ago = date.today() - timedelta(days=30)
    
    query = db.query(
        ServiceType.service_name,
        func.count(ServiceUsage.usage_id).label('usage_count')
    ).join(
        ServiceType, ServiceUsage.service_type_id == ServiceType.service_type_id
    ).filter(
        ServiceUsage.service_date >= thirty_days_ago
    ).group_by(
        ServiceType.service_type_id,
        ServiceType.service_name
    )
    
    data = query.all()
    
    return [
        {
            "service_name": row[0],
            "usage_count": row[1]
        }
        for row in data
    ]

@router.get("/monthly-revenue")
def get_monthly_revenue(
    year: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """월별 매출 데이터 조회"""
    if year is None:
        year = date.today().year
    
    # 월별 매출 집계
    query = db.query(
        extract('month', Payment.payment_date).label('month'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        extract('year', Payment.payment_date) == year
    ).group_by(
        extract('month', Payment.payment_date)
    ).order_by('month')
    
    data = query.all()
    
    # 12개월 데이터 생성 (데이터가 없는 달은 0으로)
    monthly_data = {row[0]: float(row[1]) for row in data}
    
    return [
        {
            "month": month,
            "revenue": monthly_data.get(month, 0)
        }
        for month in range(1, 13)
    ]

@router.get("/recent-activities")
def get_recent_activities(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """최근 활동 내역"""
    # 최근 결제
    recent_payments = db.query(
        Payment.payment_date,
        Payment.amount,
        Customer.name
    ).join(
        Customer, Payment.customer_id == Customer.customer_id
    ).order_by(
        Payment.payment_date.desc()
    ).limit(5).all()
    
    # 최근 서비스 이용
    recent_services = db.query(
        ServiceUsage.service_date,
        ServiceType.service_name.label('service_name'),
        Customer.name.label('customer_name')
    ).join(
        Customer, ServiceUsage.customer_id == Customer.customer_id
    ).join(
        ServiceType, ServiceUsage.service_type_id == ServiceType.service_type_id
    ).order_by(
        ServiceUsage.service_date.desc()
    ).limit(5).all()
    
    activities = []
    
    # 결제 활동
    for payment in recent_payments:
        activities.append({
            "type": "payment",
            "date": payment.payment_date.isoformat(),
            "description": f"{payment.name}님 결제",
            "amount": float(payment.amount)
        })
    
    # 서비스 이용 활동
    for service in recent_services:
        activities.append({
            "type": "service",
            "date": service.service_date.isoformat(),
            "description": f"{service.customer_name}님 {service.service_name} 이용",
            "amount": None
        })
    
    # 날짜순 정렬
    activities.sort(key=lambda x: x["date"], reverse=True)
    
    return activities[:limit]

@router.get("/weekly-stats")
def get_weekly_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """주간 통계 조회 - 최적화 버전"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # 이번 주 월요일
    week_end = week_start + timedelta(days=6)  # 이번 주 일요일
    
    # 🚀 최적화: 2개의 쿼리로 통합
    
    # 1. 방문 상담 통계
    new_consultation_visits = db.query(func.count(LeadConsultationHistory.history_id)).filter(
        and_(
            LeadConsultationHistory.consultation_date >= week_start,
            LeadConsultationHistory.consultation_date <= week_end,
            LeadConsultationHistory.consultation_type == '방문상담'
        )
    ).scalar() or 0
    
    # 2. 결제 통계 (단일 쿼리로 3개 값 조회)
    from sqlalchemy import case
    payment_stats = db.query(
        func.count(func.distinct(Payment.customer_id)).label('paying_customers'),
        func.sum(Payment.amount).label('weekly_revenue'),
        func.avg(Payment.amount).label('average_payment')
    ).filter(
        and_(
            Payment.payment_date >= week_start,
            Payment.payment_date <= week_end
        )
    ).first()
    
    # 결과 처리
    paying_customers = payment_stats.paying_customers or 0
    weekly_revenue = float(payment_stats.weekly_revenue or 0)
    average_payment = float(payment_stats.average_payment or 0)
    
    # 전환율 계산
    conversion_rate = (paying_customers / new_consultation_visits * 100) if new_consultation_visits > 0 else 0
    
    return {
        "new_consultation_visits": new_consultation_visits,
        "conversion_rate": round(conversion_rate, 1),
        "paying_customers": paying_customers,
        "average_payment": average_payment,
        "weekly_revenue": weekly_revenue,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat()
    }