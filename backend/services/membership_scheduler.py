"""
회원 등급 및 상태 자동 업데이트 스케줄러
"""

import asyncio
from datetime import datetime, date
from sqlalchemy import select, func
from sqlalchemy.orm import Session
import json
import logging

from core.database import SessionLocal
from models.customer import Customer
from models.system import SystemSettings
from models.payment import Payment

logger = logging.getLogger(__name__)

class MembershipScheduler:
    """회원 등급 및 상태 자동 업데이트 스케줄러"""

    def __init__(self, interval_hours: int = 24):
        """
        Args:
            interval_hours: 업데이트 주기 (시간 단위, 기본값: 24시간)
        """
        self.interval_hours = interval_hours
        self.is_running = False

    async def start(self):
        """스케줄러 시작"""
        self.is_running = True
        logger.info("Membership scheduler started")

        while self.is_running:
            try:
                await self.update_all_customers()
                await asyncio.sleep(self.interval_hours * 3600)  # 시간을 초로 변환
            except Exception as e:
                logger.error(f"Error in membership scheduler: {e}")
                await asyncio.sleep(300)  # 에러 발생 시 5분 후 재시도

    def stop(self):
        """스케줄러 중지"""
        self.is_running = False
        logger.info("Membership scheduler stopped")

    async def update_all_customers(self):
        """모든 고객의 등급 및 상태 업데이트"""
        db = SessionLocal()
        try:
            logger.info("Starting customer membership update...")

            # 회원 등급 기준 조회
            criteria_setting = db.query(SystemSettings).filter(
                SystemSettings.setting_key == "membership_criteria"
            ).first()

            if not criteria_setting:
                logger.warning("No membership criteria found in settings")
                return

            criteria = json.loads(criteria_setting.setting_value)

            # 모든 고객 조회
            customers = db.query(Customer).all()
            updated_count = 0

            for customer in customers:
                try:
                    # 1. 고객 상태 업데이트
                    old_status = customer.customer_status
                    customer.update_customer_status()

                    # 2. 연간 매출 계산
                    one_year_ago = datetime.now().date().replace(year=datetime.now().year - 1)
                    annual_revenue_result = db.query(
                        func.sum(Payment.amount)
                    ).filter(
                        Payment.customer_id == customer.customer_id,
                        Payment.payment_date >= one_year_ago
                    ).scalar()

                    annual_revenue = annual_revenue_result or 0

                    # 3. 회원 등급 업데이트
                    old_level = customer.membership_level
                    customer.update_membership_level(criteria, annual_revenue)


                    # 5. 최근 방문일 업데이트
                    # Reservation 테이블에서 최근 완료된 예약 날짜 조회 (실제 방문 기준)
                    from models.reservation import Reservation, ReservationStatus
                    last_visit = db.query(Reservation).filter(
                        Reservation.customer_id == customer.customer_id,
                        Reservation.status == ReservationStatus.completed
                    ).order_by(Reservation.reservation_date.desc()).first()

                    if last_visit:
                        customer.last_visit_date = last_visit.reservation_date

                    # 6. 총 방문 횟수 업데이트
                    # 완료된 예약 횟수를 방문 횟수로 계산
                    visit_count = db.query(func.count(Reservation.reservation_id)).filter(
                        Reservation.customer_id == customer.customer_id,
                        Reservation.status == ReservationStatus.completed
                    ).scalar()
                    customer.total_visits = visit_count or 0

                    # 7. 총 매출 업데이트
                    total_revenue_result = db.query(func.sum(Payment.amount)).filter(
                        Payment.customer_id == customer.customer_id
                    ).scalar()
                    customer.total_revenue = total_revenue_result or 0

                    # 변경 사항 로그
                    if (old_status != customer.customer_status or
                        old_level != customer.membership_level):
                        logger.info(
                            f"Customer {customer.customer_id} updated: "
                            f"status {old_status}->{customer.customer_status}, "
                            f"level {old_level}->{customer.membership_level}"
                        )

                    updated_count += 1

                except Exception as e:
                    logger.error(f"Error updating customer {customer.customer_id}: {e}")
                    continue

            db.commit()
            logger.info(f"Customer membership update completed. Updated {updated_count} customers.")

        except Exception as e:
            logger.error(f"Error in update_all_customers: {e}")
            db.rollback()
        finally:
            db.close()

# 싱글톤 인스턴스
membership_scheduler = MembershipScheduler()

async def start_membership_scheduler():
    """스케줄러 시작 (FastAPI startup 이벤트에서 호출)"""
    asyncio.create_task(membership_scheduler.start())

def stop_membership_scheduler():
    """스케줄러 중지 (FastAPI shutdown 이벤트에서 호출)"""
    membership_scheduler.stop()
