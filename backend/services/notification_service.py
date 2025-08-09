"""알림 서비스"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
from models.notification import Notification, NotificationSettings, NotificationType, NotificationPriority
from models.user import User
from models.package import PackagePurchase
from models.customer import Customer
from sqlalchemy.orm import selectinload
from schemas.notification import NotificationCreate, NotificationUpdate
from utils.error_handlers import ErrorResponses
from core.logging_config import get_logger

logger = get_logger(__name__)


class NotificationService:
    """알림 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        notification_data: NotificationCreate,
        send_immediately: bool = True
    ) -> Notification:
        """알림 생성"""
        # 알림 생성
        notification = Notification(**notification_data.model_dump())
        
        # 즉시 발송 설정
        if send_immediately and not notification.scheduled_for:
            notification.is_sent = True
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        logger.info(f"알림 생성: {notification.notification_id} - {notification.title}")
        return notification
    
    def create_bulk_notifications(
        self,
        user_ids: List[int],
        notification_data: NotificationCreate
    ) -> List[Notification]:
        """여러 사용자에게 알림 생성"""
        notifications = []
        
        for user_id in user_ids:
            data = notification_data.model_dump()
            data['user_id'] = user_id
            notification = Notification(**data)
            notifications.append(notification)
            self.db.add(notification)
        
        self.db.commit()
        logger.info(f"{len(notifications)}개의 알림 생성")
        return notifications
    
    def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None
    ) -> List[Notification]:
        """사용자 알림 목록 조회"""
        # 임시로 빈 리스트 반환 (user_id 컬럼이 없음)
        return []
    
    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """사용자 알림 통계"""
        try:
            # 전체 알림 수 - 임시로 모든 알림 카운트
            total_query = select(func.count(Notification.notification_id))
            total = self.db.execute(total_query).scalar() or 0
            
            # 읽지 않은 알림 수 - 임시로 0 반환
            unread = 0
            
            # 타입별 통계 - 임시로 빈 딕셔너리
            by_type = {}
            
            # 우선순위별 통계 - 임시로 빈 딕셔너리  
            by_priority = {}
            
            return {
                "total": total,
                "unread": unread,
                "by_type": by_type,
                "by_priority": by_priority
            }
        except Exception as e:
            logger.error(f"알림 통계 조회 중 오류: {str(e)}")
            # 에러 시 기본값 반환
            return {
                "total": 0,
                "unread": 0,
                "by_type": {},
                "by_priority": {}
            }
    
    def mark_as_read(self, notification_id: int, user_id: int) -> Notification:
        """알림 읽음 처리"""
        # user_id 컬럼이 없으므로 notification_id로만 조회
        query = select(Notification).where(
            Notification.notification_id == notification_id
        )
        result = self.db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise ErrorResponses.not_found("알림", notification_id)
        
        notification.is_read = True
        notification.read_at = datetime.now()
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def mark_all_as_read(self, user_id: int) -> int:
        """모든 알림 읽음 처리"""
        # user_id 컬럼이 없으므로 모든 읽지 않은 알림 처리
        query = select(Notification).where(
            Notification.is_read == False
        )
        result = self.db.execute(query)
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.now()
            count += 1
        
        self.db.commit()
        return count
    
    def delete_notification(self, notification_id: int, user_id: int):
        """알림 삭제"""
        # user_id 컬럼이 없으므로 notification_id로만 조회
        query = select(Notification).where(
            Notification.notification_id == notification_id
        )
        result = self.db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise ErrorResponses.not_found("알림", notification_id)
        
        self.db.delete(notification)
        self.db.commit()
    
    def get_or_create_settings(self, user_id: int) -> NotificationSettings:
        """사용자 알림 설정 조회 또는 생성"""
        query = select(NotificationSettings).where(
            NotificationSettings.user_id == user_id
        )
        result = self.db.execute(query)
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings
    
    def update_settings(
        self,
        user_id: int,
        settings_data: Dict[str, Any]
    ) -> NotificationSettings:
        """알림 설정 업데이트"""
        settings = self.get_or_create_settings(user_id)
        
        for key, value in settings_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        self.db.commit()
        self.db.refresh(settings)
        return settings
    
    # 특정 이벤트에 대한 알림 생성 메서드들
    
    def notify_package_expiry(self, package_id: int, days_until_expiry: int):
        """패키지 만료 알림"""
        # 패키지 정보 조회
        package_query = select(PackagePurchase).where(
            PackagePurchase.purchase_id == package_id
        ).options(selectinload(PackagePurchase.customer))
        
        result = self.db.execute(package_query)
        package = result.scalar_one_or_none()
        
        if not package:
            return
        
        # 알림 생성
        notification_data = NotificationCreate(
            user_id=1,  # TODO: 실제 담당 직원 ID로 변경
            type=NotificationType.PACKAGE,
            title=f"패키지 만료 {days_until_expiry}일 전",
            message=f"{package.customer.name}님의 {package.package_name} 패키지가 {days_until_expiry}일 후 만료됩니다.",
            priority=NotificationPriority.HIGH if days_until_expiry <= 3 else NotificationPriority.MEDIUM,
            action_url=f"/packages?customer_id={package.customer_id}",
            related_id=package_id
        )
        
        self.create_notification(notification_data)
    
    def notify_new_customer(self, customer_id: int):
        """신규 고객 등록 알림"""
        # 고객 정보 조회
        customer_query = select(Customer).where(Customer.customer_id == customer_id)
        result = self.db.execute(customer_query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return
        
        # 관리자들에게 알림
        admin_query = select(User.user_id).where(User.role == "admin")
        admin_result = self.db.execute(admin_query)
        admin_ids = [row[0] for row in admin_result.all()]
        
        notification_data = NotificationCreate(
            type=NotificationType.CUSTOMER,
            title="신규 고객 등록",
            message=f"{customer.name}님이 신규 등록되었습니다.",
            priority=NotificationPriority.LOW,
            action_url=f"/customers/{customer_id}",
            related_id=customer_id
        )
        
        self.create_bulk_notifications(admin_ids, notification_data)