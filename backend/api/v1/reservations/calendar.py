from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import date, timedelta

from core.database import get_db
from core.auth import get_current_user
from models import Reservation, ReservationStatus, ServiceType, User

router = APIRouter()

@router.get("")
def get_calendar_view(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    staff_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """월별 예약 캘린더 데이터"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    query = db.query(
        Reservation.reservation_date,
        func.count(Reservation.reservation_id).label('total_reservations'),
        func.count(func.distinct(Reservation.customer_id)).label('unique_customers')
    ).filter(
        and_(
            Reservation.reservation_date >= start_date,
            Reservation.reservation_date <= end_date,
            Reservation.status.in_(['pending', 'confirmed'])
        )
    )

    if staff_id:
        query = query.filter(Reservation.staff_id == staff_id)

    daily_stats = query.group_by(Reservation.reservation_date).all()

    # 서비스별 통계
    service_query = db.query(
        Reservation.reservation_date,
        ServiceType.service_name,
        func.count(Reservation.reservation_id).label('count')
    ).join(
        ServiceType
    ).filter(
        and_(
            Reservation.reservation_date >= start_date,
            Reservation.reservation_date <= end_date,
            Reservation.status.in_(['pending', 'confirmed'])
        )
    )

    if staff_id:
        service_query = service_query.filter(Reservation.staff_id == staff_id)

    service_stats = service_query.group_by(
        Reservation.reservation_date,
        ServiceType.service_name
    ).all()

    # 데이터 정리
    calendar_data = {}

    for stat in daily_stats:
        date_str = stat.reservation_date.isoformat()
        calendar_data[date_str] = {
            "total_reservations": stat.total_reservations,
            "unique_customers": stat.unique_customers,
            "services": {}
        }

    for stat in service_stats:
        date_str = stat.reservation_date.isoformat()
        if date_str in calendar_data:
            calendar_data[date_str]["services"][stat.service_name] = stat.count

    return calendar_data
