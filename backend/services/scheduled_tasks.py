"""스케줄된 작업"""
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from core.database import SessionLocal
from models.package import PackagePurchase
from sqlalchemy.orm import selectinload
from models.notification import NotificationType, NotificationPriority
from schemas.notification import NotificationCreate
from services.notification_service import NotificationService
from core.logging_config import get_logger

logger = get_logger(__name__)


class ScheduledTasks:
    """스케줄된 작업 클래스"""
    
    @staticmethod
    def check_package_expiry():
        """패키지 만료 확인 및 알림 생성"""
        db = SessionLocal()
        try:
            notification_service = NotificationService(db)
            today = date.today()
            
            # 7일 후 만료 예정 패키지
            seven_days_later = today + timedelta(days=7)
            query_7days = select(PackagePurchase).where(
                and_(
                    PackagePurchase.expiry_date == seven_days_later,
                    PackagePurchase.remaining_sessions > 0
                )
            ).options(selectinload(PackagePurchase.customer))
            packages_7days = db.execute(query_7days).scalars().all()
            
            for package in packages_7days:
                notification_data = NotificationCreate(
                    user_id=1,  # TODO: 실제 담당 직원 ID로 변경
                    type=NotificationType.PACKAGE,
                    title="패키지 만료 7일 전",
                    message=f"{package.customer.name}님의 {package.package_name} 패키지가 7일 후 만료됩니다. (잔여: {package.remaining_sessions}회)",
                    priority=NotificationPriority.MEDIUM,
                    action_url=f"/packages?customer_id={package.customer_id}",
                    related_id=package.purchase_id
                )
                notification_service.create_notification(notification_data)
                logger.info(f"패키지 만료 7일 전 알림 생성: {package.purchase_id}")
            
            # 3일 후 만료 예정 패키지
            three_days_later = today + timedelta(days=3)
            query_3days = select(PackagePurchase).where(
                and_(
                    PackagePurchase.expiry_date == three_days_later,
                    PackagePurchase.remaining_sessions > 0
                )
            ).options(selectinload(PackagePurchase.customer))
            packages_3days = db.execute(query_3days).scalars().all()
            
            for package in packages_3days:
                notification_data = NotificationCreate(
                    user_id=1,  # TODO: 실제 담당 직원 ID로 변경
                    type=NotificationType.PACKAGE,
                    title="패키지 만료 3일 전 ⚠️",
                    message=f"{package.customer.name}님의 {package.package_name} 패키지가 3일 후 만료됩니다! (잔여: {package.remaining_sessions}회)",
                    priority=NotificationPriority.HIGH,
                    action_url=f"/packages?customer_id={package.customer_id}",
                    related_id=package.purchase_id
                )
                notification_service.create_notification(notification_data)
                logger.info(f"패키지 만료 3일 전 알림 생성: {package.purchase_id}")
            
            # 오늘 만료되는 패키지
            query_today = select(PackagePurchase).where(
                and_(
                    PackagePurchase.expiry_date == today,
                    PackagePurchase.remaining_sessions > 0
                )
            ).options(selectinload(PackagePurchase.customer))
            packages_today = db.execute(query_today).scalars().all()
            
            for package in packages_today:
                notification_data = NotificationCreate(
                    user_id=1,  # TODO: 실제 담당 직원 ID로 변경
                    type=NotificationType.PACKAGE,
                    title="패키지 오늘 만료 🚨",
                    message=f"{package.customer.name}님의 {package.package_name} 패키지가 오늘 만료됩니다! (잔여: {package.remaining_sessions}회)",
                    priority=NotificationPriority.HIGH,
                    action_url=f"/packages?customer_id={package.customer_id}",
                    related_id=package.purchase_id
                )
                notification_service.create_notification(notification_data)
                logger.info(f"패키지 당일 만료 알림 생성: {package.purchase_id}")
            
            # 잔여 횟수 3회 이하 패키지
            query_low_sessions = select(PackagePurchase).where(
                and_(
                    PackagePurchase.remaining_sessions > 0,
                    PackagePurchase.remaining_sessions <= 3,
                    PackagePurchase.expiry_date > today
                )
            ).options(selectinload(PackagePurchase.customer))
            packages_low = db.execute(query_low_sessions).scalars().all()
            
            for package in packages_low:
                # 이미 최근에 알림을 보냈는지 확인 (중복 방지)
                # TODO: 구현 필요
                
                notification_data = NotificationCreate(
                    user_id=1,  # TODO: 실제 담당 직원 ID로 변경
                    type=NotificationType.PACKAGE,
                    title="패키지 잔여 횟수 부족",
                    message=f"{package.customer.name}님의 {package.package_name} 패키지 잔여 횟수가 {package.remaining_sessions}회 남았습니다.",
                    priority=NotificationPriority.MEDIUM,
                    action_url=f"/packages?customer_id={package.customer_id}",
                    related_id=package.purchase_id
                )
                notification_service.create_notification(notification_data)
                logger.info(f"패키지 잔여 횟수 부족 알림 생성: {package.purchase_id}")
            
            logger.info("패키지 만료 확인 작업 완료")
            
        except Exception as e:
            logger.error(f"패키지 만료 확인 중 오류: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def send_daily_report():
        """일일 매출 리포트 알림"""
        db = SessionLocal()
        try:
            notification_service = NotificationService(db)
            
            # 어제 날짜
            yesterday = date.today() - timedelta(days=1)
            
            # 어제 매출 계산
            from models.payment import Payment
            from sqlalchemy import func
            
            revenue_query = select(func.sum(Payment.amount)).where(
                Payment.payment_date == yesterday
            )
            yesterday_revenue = db.execute(revenue_query).scalar() or 0
            
            # 결제 건수
            count_query = select(func.count(Payment.payment_id)).where(
                Payment.payment_date == yesterday
            )
            payment_count = db.execute(count_query).scalar() or 0
            
            # 관리자들에게 알림
            from models.user import User
            admin_query = select(User.user_id).where(User.role == "admin")
            admin_ids = [row[0] for row in db.execute(admin_query).all()]
            
            notification_data = NotificationCreate(
                type=NotificationType.SYSTEM,
                title="일일 매출 리포트 📊",
                message=f"{yesterday.strftime('%Y-%m-%d')} 매출: {yesterday_revenue:,}원 ({payment_count}건)",
                priority=NotificationPriority.LOW,
                action_url="/reports"
            )
            
            notification_service.create_bulk_notifications(admin_ids, notification_data)
            logger.info(f"일일 매출 리포트 알림 생성: {yesterday}")
            
        except Exception as e:
            logger.error(f"일일 리포트 생성 중 오류: {str(e)}")
        finally:
            db.close()