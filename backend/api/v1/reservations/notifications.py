from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import date, datetime, timedelta

from core.database import get_db
from core.auth import get_current_user
from models.reservation import Reservation, ReservationStatus
from models.user import User
from models.reservation import KakaoMessageLog
from services.kakao_service import kakao_service, message_builder

router = APIRouter()

@router.post("/send-reminders")
def send_tomorrow_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """내일 예약 리마인더 발송"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 사용할 수 있습니다."
        )

    tomorrow = date.today() + timedelta(days=1)

    # 내일 예약 중 리마인더 미발송 건 조회
    reservations = db.query(Reservation).options(
        joinedload(Reservation.customer),
        joinedload(Reservation.service_type)
    ).filter(
        and_(
            Reservation.reservation_date == tomorrow,
            Reservation.status == ReservationStatus.confirmed,
            Reservation.reminder_sent == False
        )
    ).all()

    success_count = 0
    fail_count = 0

    for reservation in reservations:
        if not reservation.customer.phone:
            continue

        try:
            # 알림톡 발송
            datetime_str = f"{reservation.reservation_date.strftime('%Y년 %m월 %d일')} {reservation.reservation_time.strftime('%H:%M')}"

            template_args = message_builder.build_reminder(
                customer_name=reservation.customer.name,
                reservation_datetime=datetime_str,
                service_name=reservation.service_type.service_name
            )

            result = kakao_service.send_alimtalk(
                phone_number=reservation.customer.phone,
                template_code="REMINDER_001",  # 실제 승인된 템플릿 코드
                template_args=template_args
            )

            # 발송 이력 저장
            log = KakaoMessageLog(
                reservation_id=reservation.reservation_id,
                customer_id=reservation.customer_id,
                template_code="REMINDER_001",
                phone_number=reservation.customer.phone,
                message_type="alimtalk",
                status="success" if result["success"] else "failed",
                message_id=result.get("message_id"),
                content=f"내일 {datetime_str} 예약 리마인더",
                variables_used=template_args,
                sent_at=datetime.now() if result["success"] else None,
                error_code=result.get("error_code"),
                error_message=result.get("error_message")
            )
            db.add(log)

            if result["success"]:
                reservation.reminder_sent = True
                success_count += 1
            else:
                fail_count += 1

        except Exception as e:
            fail_count += 1
            print(f"리마인더 발송 오류: {str(e)}")

    db.commit()

    return {
        "total": len(reservations),
        "success": success_count,
        "failed": fail_count
    }

# 알림톡 발송 헬퍼 함수들
def send_reservation_confirmation(db: Session, reservation: Reservation):
    """예약 확인 알림톡 발송"""
    datetime_str = f"{reservation.reservation_date.strftime('%Y년 %m월 %d일')} {reservation.reservation_time.strftime('%H:%M')}"

    template_args = message_builder.build_reservation_confirmation(
        customer_name=reservation.customer.name,
        reservation_datetime=datetime_str,
        service_name=reservation.service_type.service_name,
        staff_name=reservation.staff.name if reservation.staff else "미정"
    )

    result = kakao_service.send_alimtalk(
        phone_number=reservation.customer.phone,
        template_code="RESERVATION_CONFIRM_001",  # 실제 승인된 템플릿 코드
        template_args=template_args,
        fallback_message=f"{reservation.customer.name}님, AIBIO Center 예약이 확인되었습니다. {datetime_str}"
    )

    # 발송 이력 저장
    log = KakaoMessageLog(
        reservation_id=reservation.reservation_id,
        customer_id=reservation.customer_id,
        template_code="RESERVATION_CONFIRM_001",
        phone_number=reservation.customer.phone,
        message_type="alimtalk",
        status="success" if result["success"] else "failed",
        message_id=result.get("message_id"),
        content=f"예약 확인: {datetime_str}",
        variables_used=template_args,
        sent_at=datetime.now() if result["success"] else None,
        error_code=result.get("error_code"),
        error_message=result.get("error_message")
    )
    db.add(log)

    if result["success"]:
        reservation.confirmation_sent = True

    db.commit()

    return result

def send_reservation_change_notification(db: Session, reservation: Reservation, old_datetime: str, new_datetime: str):
    """예약 변경 알림톡 발송"""
    template_args = message_builder.build_change_notification(
        customer_name=reservation.customer.name,
        old_datetime=old_datetime,
        new_datetime=new_datetime,
        service_name=reservation.service_type.service_name
    )

    result = kakao_service.send_alimtalk(
        phone_number=reservation.customer.phone,
        template_code="RESERVATION_CHANGE_001",
        template_args=template_args
    )

    # 발송 이력 저장
    log = KakaoMessageLog(
        reservation_id=reservation.reservation_id,
        customer_id=reservation.customer_id,
        template_code="RESERVATION_CHANGE_001",
        phone_number=reservation.customer.phone,
        message_type="alimtalk",
        status="success" if result["success"] else "failed",
        message_id=result.get("message_id"),
        content=f"예약 변경: {old_datetime} → {new_datetime}",
        variables_used=template_args,
        sent_at=datetime.now() if result["success"] else None,
        error_code=result.get("error_code"),
        error_message=result.get("error_message")
    )
    db.add(log)
    db.commit()

    return result

def send_reservation_cancellation(db: Session, reservation: Reservation):
    """예약 취소 알림톡 발송"""
    datetime_str = f"{reservation.reservation_date.strftime('%Y년 %m월 %d일')} {reservation.reservation_time.strftime('%H:%M')}"

    template_args = message_builder.build_cancellation(
        customer_name=reservation.customer.name,
        reservation_datetime=datetime_str,
        service_name=reservation.service_type.service_name,
        cancel_reason=reservation.cancel_reason or "고객 요청"
    )

    result = kakao_service.send_alimtalk(
        phone_number=reservation.customer.phone,
        template_code="RESERVATION_CANCEL_001",
        template_args=template_args
    )

    # 발송 이력 저장
    log = KakaoMessageLog(
        reservation_id=reservation.reservation_id,
        customer_id=reservation.customer_id,
        template_code="RESERVATION_CANCEL_001",
        phone_number=reservation.customer.phone,
        message_type="alimtalk",
        status="success" if result["success"] else "failed",
        message_id=result.get("message_id"),
        content=f"예약 취소: {datetime_str}",
        variables_used=template_args,
        sent_at=datetime.now() if result["success"] else None,
        error_code=result.get("error_code"),
        error_message=result.get("error_message")
    )
    db.add(log)
    db.commit()

    return result
