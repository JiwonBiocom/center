#!/usr/bin/env python3
"""
고객 방문일 데이터 업데이트 스크립트
- 기존 서비스 이용 기반에서 예약 완료 기반으로 변경
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date
import logging

from core.database import SessionLocal
from models.customer import Customer
from models.reservation import Reservation, ReservationStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_customer_visit_dates():
    """모든 고객의 방문일과 방문 횟수를 예약 기반으로 업데이트"""
    db = SessionLocal()
    try:
        logger.info("Starting customer visit dates update...")

        # 모든 고객 조회
        customers = db.query(Customer).all()
        updated_count = 0

        for customer in customers:
            # 1. 마지막 완료된 예약 찾기
            last_completed_reservation = db.query(Reservation).filter(
                Reservation.customer_id == customer.customer_id,
                Reservation.status == ReservationStatus.completed
            ).order_by(Reservation.reservation_date.desc()).first()

            # 2. 완료된 예약 횟수 계산
            completed_visits = db.query(func.count(Reservation.reservation_id)).filter(
                Reservation.customer_id == customer.customer_id,
                Reservation.status == ReservationStatus.completed
            ).scalar() or 0

            # 3. 데이터 업데이트
            old_last_visit = customer.last_visit_date
            old_total_visits = customer.total_visits

            if last_completed_reservation:
                customer.last_visit_date = last_completed_reservation.reservation_date
            else:
                # 완료된 예약이 없는 경우
                customer.last_visit_date = None

            customer.total_visits = completed_visits

            # 4. 고객 상태 업데이트
            old_status = customer.customer_status
            customer.update_customer_status()

            # 5. 위험 수준 업데이트
            old_risk = customer.risk_level
            customer.update_risk_level(complaint_count=0)

            # 변경사항 로그
            if (old_last_visit != customer.last_visit_date or
                old_total_visits != customer.total_visits or
                old_status != customer.customer_status or
                old_risk != customer.risk_level):
                logger.info(
                    f"Customer {customer.customer_id} ({customer.name}) updated: "
                    f"last_visit: {old_last_visit} -> {customer.last_visit_date}, "
                    f"total_visits: {old_total_visits} -> {customer.total_visits}, "
                    f"status: {old_status} -> {customer.customer_status}, "
                    f"risk: {old_risk} -> {customer.risk_level}"
                )
                updated_count += 1

        db.commit()
        logger.info(f"Update completed. Updated {updated_count} customers out of {len(customers)} total.")

        # 통계 출력
        active_count = db.query(func.count(Customer.customer_id)).filter(
            Customer.customer_status == 'active'
        ).scalar()
        inactive_count = db.query(func.count(Customer.customer_id)).filter(
            Customer.customer_status == 'inactive'
        ).scalar()
        dormant_count = db.query(func.count(Customer.customer_id)).filter(
            Customer.customer_status == 'dormant'
        ).scalar()

        logger.info(f"\nCustomer status summary:")
        logger.info(f"- Active: {active_count}")
        logger.info(f"- Inactive: {inactive_count}")
        logger.info(f"- Dormant: {dormant_count}")

    except Exception as e:
        logger.error(f"Error updating customer visit dates: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_customer_visit_dates()
