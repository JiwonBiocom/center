from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import date, datetime, timedelta, time as datetime_time

from core.database import get_db
from core.auth import get_current_user
from models import Reservation, ReservationStatus, User

router = APIRouter()

@router.get("/available")
def get_available_slots(
    date: date = Query(...),
    service_type_id: int = Query(...),
    staff_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예약 가능한 시간대 조회"""
    # 영업 시간 (설정에서 가져와야 하지만 일단 하드코딩)
    business_start = datetime_time(9, 0)  # 09:00
    business_end = datetime_time(18, 0)   # 18:00
    slot_duration = 15  # 15분 단위

    # 해당 날짜의 기존 예약 조회
    existing_reservations = db.query(Reservation).filter(
        and_(
            Reservation.reservation_date == date,
            Reservation.status.in_(['pending', 'confirmed'])
        )
    )

    if staff_id:
        existing_reservations = existing_reservations.filter(Reservation.staff_id == staff_id)

    existing_times = [r.reservation_time for r in existing_reservations.all()]

    # 가능한 시간대 생성
    available_slots = []
    current_time = datetime.combine(date, business_start)
    end_time = datetime.combine(date, business_end)

    while current_time < end_time:
        slot_time = current_time.time()
        if slot_time not in existing_times:
            available_slots.append({
                "date": date,
                "time": slot_time,
                "staff_id": staff_id
            })
        current_time += timedelta(minutes=slot_duration)

    return available_slots
