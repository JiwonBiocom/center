from sqlalchemy import Column, Integer, String, DateTime, Date, Time, ForeignKey, Boolean, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from core.database import Base

class ReservationStatus(str, enum.Enum):
    pending = "pending"          # 예약 대기
    confirmed = "confirmed"      # 예약 확정
    cancelled = "cancelled"      # 예약 취소
    completed = "completed"      # 서비스 완료
    no_show = "no_show"         # 노쇼

class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    service_type_id = Column(Integer, ForeignKey("service_types.service_type_id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("users.user_id"))

    # 예약 일시
    reservation_date = Column(Date, nullable=False, index=True)
    reservation_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=60)  # 서비스 소요 시간

    # 상태 관리
    status = Column(Enum(ReservationStatus), default=ReservationStatus.pending, nullable=False, index=True)

    # 예약 메모
    customer_request = Column(Text)  # 고객 요청사항
    internal_memo = Column(Text)     # 내부 메모

    # 알림 관련
    reminder_sent = Column(Boolean, default=False)
    confirmation_sent = Column(Boolean, default=False)

    # 메타 정보
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(50))
    cancelled_at = Column(DateTime)
    cancelled_by = Column(String(50))
    cancel_reason = Column(Text)

    # Relationships
    customer = relationship("Customer", backref="reservations")
    service_type = relationship("ServiceType", backref="reservations")
    staff = relationship("User", backref="assigned_reservations")

class ReservationSlot(Base):
    """예약 가능한 시간대 관리"""
    __tablename__ = "reservation_slots"

    slot_id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.user_id"))
    day_of_week = Column(Integer)  # 0=월요일, 6=일요일
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

    # 특정 날짜의 예외 처리
    specific_date = Column(Date)  # NULL이면 매주 반복, 값이 있으면 특정 날짜

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", backref="schedule_slots")

class KakaoTemplate(Base):
    """카카오 알림톡 템플릿 관리"""
    __tablename__ = "kakao_templates"

    template_id = Column(Integer, primary_key=True, index=True)
    template_code = Column(String(50), unique=True, nullable=False)  # 카카오에서 부여받은 템플릿 코드
    template_name = Column(String(100), nullable=False)
    template_type = Column(String(50))  # reservation_confirm, reminder, change, cancel
    content = Column(Text, nullable=False)
    variables = Column(JSON)  # ["고객명", "예약일시", "서비스명"] 등

    is_active = Column(Boolean, default=True)
    approved_at = Column(DateTime)  # 카카오 승인 일시

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class KakaoMessageLog(Base):
    """카카오톡 발송 이력"""
    __tablename__ = "kakao_message_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.reservation_id"))
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))

    template_code = Column(String(50))
    phone_number = Column(String(20))
    message_type = Column(String(20))  # alimtalk, friendtalk, sms

    # 발송 상태
    status = Column(String(20))  # pending, success, failed
    message_id = Column(String(100))  # 카카오 메시지 ID

    # 발송 내용
    content = Column(Text)
    variables_used = Column(JSON)

    # 발송 결과
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)

    # 에러 정보
    error_code = Column(String(50))
    error_message = Column(Text)

    # SMS 대체 발송
    fallback_status = Column(String(20))
    fallback_sent_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    reservation = relationship("Reservation", backref="kakao_messages")
    customer = relationship("Customer", backref="kakao_messages")
