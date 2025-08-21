from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from datetime import date, datetime
import logging

from core.database import get_db
from core.auth import get_current_user
from models.reservation import Reservation, ReservationStatus
from models.customer import Customer
from models.service import ServiceType, ServiceUsage
from models.user import User
from models.package import Package, PackagePurchase
from schemas.reservation import (
    ReservationCreate, ReservationUpdate, ReservationResponse, ReservationCancel
)
from services.kakao_service import kakao_service
from services.aligo_service import aligo_service, sms_templates

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[ReservationResponse])
def get_reservations(
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[ReservationStatus] = None,
    customer_id: Optional[int] = None,
    staff_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예약 목록 조회"""
    query = db.query(Reservation).options(
        joinedload(Reservation.customer),
        joinedload(Reservation.service_type),
        joinedload(Reservation.staff)
    )

    if date_from:
        query = query.filter(Reservation.reservation_date >= date_from)
    if date_to:
        query = query.filter(Reservation.reservation_date <= date_to)
    if status:
        query = query.filter(Reservation.status == status)
    if customer_id:
        query = query.filter(Reservation.customer_id == customer_id)
    if staff_id:
        query = query.filter(Reservation.staff_id == staff_id)

    reservations = query.offset(skip).limit(limit).all()

    # Response 변환
    result = []
    for r in reservations:
        reservation_dict = {
            "reservation_id": r.reservation_id,
            "customer_id": r.customer_id,
            "service_type_id": r.service_type_id,
            "staff_id": r.staff_id,
            "reservation_date": r.reservation_date,
            "reservation_time": r.reservation_time,
            "duration_minutes": r.duration_minutes,
            "status": r.status,
            "customer_request": r.customer_request,
            "internal_memo": r.internal_memo,
            "reminder_sent": r.reminder_sent,
            "confirmation_sent": r.confirmation_sent,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
            "cancelled_at": r.cancelled_at,
            "cancel_reason": r.cancel_reason,
            "customer_name": r.customer.name if r.customer else None,
            "service_name": r.service_type.service_name if r.service_type else None,
            "staff_name": r.staff.name if r.staff else None
        }
        result.append(ReservationResponse(**reservation_dict))

    return result

@router.get("/{reservation_id}", response_model=ReservationResponse)
@router.get("/{reservation_id}/", response_model=ReservationResponse)  # trailing slash 버전
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """개별 예약 조회"""
    reservation = db.query(Reservation).options(
        joinedload(Reservation.customer),
        joinedload(Reservation.service_type),
        joinedload(Reservation.staff)
    ).filter(Reservation.reservation_id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")

    return ReservationResponse(
        reservation_id=reservation.reservation_id,
        customer_id=reservation.customer_id,
        service_type_id=reservation.service_type_id,
        staff_id=reservation.staff_id,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        duration_minutes=reservation.duration_minutes,
        status=reservation.status,
        customer_request=reservation.customer_request,
        internal_memo=reservation.internal_memo,
        reminder_sent=reservation.reminder_sent,
        confirmation_sent=reservation.confirmation_sent,
        created_at=reservation.created_at,
        updated_at=reservation.updated_at,
        cancelled_at=reservation.cancelled_at,
        cancel_reason=reservation.cancel_reason,
        customer_name=reservation.customer.name if reservation.customer else None,
        service_name=reservation.service_type.service_name if reservation.service_type else None,
        staff_name=reservation.staff.name if reservation.staff else None
    )

@router.post("/", response_model=ReservationResponse)
def create_reservation(
    reservation: ReservationCreate,
    send_confirmation: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새 예약 생성 - 등록된 고객 또는 게스트 고객 모두 가능"""
    # 중복 예약 확인 - 같은 서비스 타입끼리만 체크
    existing = db.query(Reservation).filter(
        and_(
            Reservation.reservation_date == reservation.reservation_date,
            Reservation.reservation_time == reservation.reservation_time,
            Reservation.service_type_id == reservation.service_type_id,  # 같은 서비스 타입만 체크
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.confirmed])
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="해당 시간에 이미 같은 서비스의 예약이 있습니다"
        )

    # 직원 중복 확인 (staff_id가 있는 경우)
    if reservation.staff_id:
        staff_conflict = db.query(Reservation).filter(
            and_(
                Reservation.reservation_date == reservation.reservation_date,
                Reservation.reservation_time == reservation.reservation_time,
                Reservation.staff_id == reservation.staff_id,
                Reservation.status.in_([ReservationStatus.pending, ReservationStatus.confirmed])
            )
        ).first()

        if staff_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="해당 직원은 이미 다른 예약이 있습니다"
            )

    # 고객 처리: customer_id가 있으면 기존 고객, 없으면 게스트 고객 생성
    if reservation.customer_id:
        # 기존 고객
        customer = db.query(Customer).filter(Customer.customer_id == reservation.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="고객을 찾을 수 없습니다")
    elif reservation.customer_name:
        # 게스트 고객 - 먼저 같은 이름과 전화번호로 기존 고객 검색
        if reservation.customer_phone:
            customer = db.query(Customer).filter(
                Customer.name == reservation.customer_name,
                Customer.phone == reservation.customer_phone
            ).first()
        else:
            customer = None
        
        # 기존 고객이 없으면 새로 생성
        if not customer:
            customer = Customer(
                name=reservation.customer_name,
                phone=reservation.customer_phone,
                membership_level='basic',
                customer_status='active',
                memo=f"예약 시 자동 생성 ({reservation.reservation_date})"
            )
            db.add(customer)
            db.flush()  # customer_id를 얻기 위해 flush
    else:
        raise HTTPException(
            status_code=400, 
            detail="고객 ID 또는 고객 이름을 입력해주세요"
        )

    service_type = db.query(ServiceType).filter(ServiceType.service_type_id == reservation.service_type_id).first()
    if not service_type:
        raise HTTPException(status_code=404, detail="서비스 타입을 찾을 수 없습니다")

    # 예약 생성
    db_reservation = Reservation(
        customer_id=customer.customer_id,
        service_type_id=reservation.service_type_id,
        staff_id=reservation.staff_id,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        duration_minutes=reservation.duration_minutes or service_type.default_duration,
        status=ReservationStatus.pending,
        customer_request=reservation.customer_request,
        internal_memo=reservation.internal_memo
    )

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    # 확인 메시지 발송
    if send_confirmation and customer.phone:
        try:
            staff = db.query(User).filter(User.user_id == reservation.staff_id).first()
            staff_name = staff.name if staff else None

            # SMS 메시지 생성
            message = sms_templates.reservation_confirmation(
                customer_name=customer.name,
                reservation_date=str(reservation.reservation_date),
                reservation_time=str(reservation.reservation_time),
                service_name=service_type.service_name,
                staff_name=staff_name
            )

            # 알리고 SMS 발송
            result = aligo_service.send_sms(
                receiver=customer.phone,
                message=message
            )

            if result["success"]:
                db_reservation.confirmation_sent = True
                db.commit()
                logger.info(f"예약 확인 SMS 발송 성공: {customer.name} ({customer.phone})")
            else:
                logger.error(f"예약 확인 SMS 발송 실패: {result.get('error_message')}")

        except Exception as e:
            logger.error(f"확인 메시지 발송 중 오류: {e}")

    # Response 변환
    return ReservationResponse(
        reservation_id=db_reservation.reservation_id,
        customer_id=db_reservation.customer_id,
        service_type_id=db_reservation.service_type_id,
        staff_id=db_reservation.staff_id,
        reservation_date=db_reservation.reservation_date,
        reservation_time=db_reservation.reservation_time,
        duration_minutes=db_reservation.duration_minutes,
        status=db_reservation.status,
        customer_request=db_reservation.customer_request,
        internal_memo=db_reservation.internal_memo,
        reminder_sent=db_reservation.reminder_sent,
        confirmation_sent=db_reservation.confirmation_sent,
        created_at=db_reservation.created_at,
        updated_at=db_reservation.updated_at,
        cancelled_at=db_reservation.cancelled_at,
        cancel_reason=db_reservation.cancel_reason,
        customer_name=customer.name,
        service_name=service_type.service_name,
        staff_name=staff_name if 'staff_name' in locals() else None
    )

@router.put("/{reservation_id}", response_model=ReservationResponse)
@router.put("/{reservation_id}/", response_model=ReservationResponse)  # trailing slash 버전 추가
def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예약 수정"""
    db_reservation = db.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")

    # 수정 가능한 필드만 업데이트
    update_data = reservation_update.dict(exclude_unset=True)

    # 시간 변경 시 중복 확인
    if 'reservation_date' in update_data or 'reservation_time' in update_data or 'service_type_id' in update_data:
        new_date = update_data.get('reservation_date', db_reservation.reservation_date)
        new_time = update_data.get('reservation_time', db_reservation.reservation_time)
        new_service_type_id = update_data.get('service_type_id', db_reservation.service_type_id)

        # 같은 서비스 타입끼리만 체크
        existing = db.query(Reservation).filter(
            and_(
                Reservation.reservation_id != reservation_id,
                Reservation.reservation_date == new_date,
                Reservation.reservation_time == new_time,
                Reservation.service_type_id == new_service_type_id,
                Reservation.status.in_([ReservationStatus.pending, ReservationStatus.confirmed])
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="해당 시간에 이미 같은 서비스의 예약이 있습니다"
            )

        # 직원 중복 확인 (staff_id가 있는 경우)
        new_staff_id = update_data.get('staff_id', db_reservation.staff_id)
        if new_staff_id:
            staff_conflict = db.query(Reservation).filter(
                and_(
                    Reservation.reservation_id != reservation_id,
                    Reservation.reservation_date == new_date,
                    Reservation.reservation_time == new_time,
                    Reservation.staff_id == new_staff_id,
                    Reservation.status.in_([ReservationStatus.pending, ReservationStatus.confirmed])
                )
            ).first()

            if staff_conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="해당 직원은 이미 다른 예약이 있습니다"
                )

    # 업데이트 실행
    for field, value in update_data.items():
        setattr(db_reservation, field, value)

    db_reservation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_reservation)

    # 관련 정보 조회
    customer = db.query(Customer).filter(Customer.customer_id == db_reservation.customer_id).first()
    service_type = db.query(ServiceType).filter(ServiceType.service_type_id == db_reservation.service_type_id).first()
    staff = db.query(User).filter(User.user_id == db_reservation.staff_id).first()

    return ReservationResponse(
        reservation_id=db_reservation.reservation_id,
        customer_id=db_reservation.customer_id,
        service_type_id=db_reservation.service_type_id,
        staff_id=db_reservation.staff_id,
        reservation_date=db_reservation.reservation_date,
        reservation_time=db_reservation.reservation_time,
        duration_minutes=db_reservation.duration_minutes,
        status=db_reservation.status,
        customer_request=db_reservation.customer_request,
        internal_memo=db_reservation.internal_memo,
        reminder_sent=db_reservation.reminder_sent,
        confirmation_sent=db_reservation.confirmation_sent,
        created_at=db_reservation.created_at,
        updated_at=db_reservation.updated_at,
        cancelled_at=db_reservation.cancelled_at,
        cancel_reason=db_reservation.cancel_reason,
        customer_name=customer.name if customer else None,
        service_name=service_type.service_name if service_type else None,
        staff_name=staff.name if staff else None
    )

@router.post("/{reservation_id}/cancel")
@router.post("/{reservation_id}/cancel/")  # trailing slash 버전 추가
def cancel_reservation(
    reservation_id: int,
    cancel_data: ReservationCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예약 취소"""
    db_reservation = db.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")

    if db_reservation.status == 'cancelled':
        raise HTTPException(status_code=400, detail="이미 취소된 예약입니다")

    # 취소 처리
    db_reservation.status = 'cancelled'
    db_reservation.cancelled_at = datetime.utcnow()
    db_reservation.cancel_reason = cancel_data.reason
    db_reservation.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "예약이 취소되었습니다"}

@router.post("/{reservation_id}/confirm")
@router.post("/{reservation_id}/confirm/")  # trailing slash 버전 추가
def confirm_reservation(
    reservation_id: int,
    send_confirmation: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예약 확정"""
    db_reservation = db.query(Reservation).options(
        joinedload(Reservation.customer),
        joinedload(Reservation.service_type),
        joinedload(Reservation.staff)
    ).filter(Reservation.reservation_id == reservation_id).first()

    if not db_reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")

    if db_reservation.status == 'confirmed':
        raise HTTPException(status_code=400, detail="이미 확정된 예약입니다")

    if db_reservation.status == 'cancelled':
        raise HTTPException(status_code=400, detail="취소된 예약은 확정할 수 없습니다")

    # 확정 처리
    db_reservation.status = 'confirmed'
    db_reservation.updated_at = datetime.utcnow()

    db.commit()

    # 확정 SMS 발송
    if send_confirmation and db_reservation.customer.phone:
        try:
            # SMS 메시지 생성
            message = sms_templates.reservation_confirmation(
                customer_name=db_reservation.customer.name,
                reservation_date=str(db_reservation.reservation_date),
                reservation_time=str(db_reservation.reservation_time),
                service_name=db_reservation.service_type.service_name,
                staff_name=db_reservation.staff.name if db_reservation.staff else None
            )

            # 알리고 SMS 발송
            result = aligo_service.send_sms(
                receiver=db_reservation.customer.phone,
                message=message
            )

            if result["success"]:
                logger.info(f"예약 확정 SMS 발송 성공: {db_reservation.customer.name} ({db_reservation.customer.phone})")
            else:
                logger.error(f"예약 확정 SMS 발송 실패: {result.get('error_message')}")

        except Exception as e:
            logger.error(f"확정 SMS 발송 중 오류: {e}")

    return {"message": "예약이 확정되었습니다"}

@router.delete("/{reservation_id}")
@router.delete("/{reservation_id}/")  # trailing slash 버전 추가
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예약 삭제 - 취소된 예약만 삭제 가능"""
    db_reservation = db.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")

    # 취소된 예약만 삭제 가능
    if db_reservation.status != 'cancelled':
        raise HTTPException(
            status_code=400,
            detail="취소된 예약만 삭제할 수 있습니다. 먼저 예약을 취소해주세요."
        )

    # 완료된 예약은 삭제 불가 (서비스 이용 기록과 연결되어 있을 수 있음)
    if db_reservation.status == 'completed':
        raise HTTPException(
            status_code=400,
            detail="완료된 예약은 삭제할 수 없습니다."
        )

    # 관리자만 삭제 가능
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="예약 삭제는 관리자만 가능합니다."
        )

    # 삭제 실행
    db.delete(db_reservation)
    db.commit()

    logger.info(f"예약 삭제됨: ID {reservation_id} by {current_user.name}")

    return {"message": "예약이 삭제되었습니다"}

@router.post("/{reservation_id}/complete")
@router.post("/{reservation_id}/complete/")  # trailing slash 버전 추가
def complete_reservation(
    reservation_id: int,
    package_id: Optional[int] = None,
    session_details: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예약 완료 및 서비스 이용 기록 자동 생성"""
    db_reservation = db.query(Reservation).options(
        joinedload(Reservation.customer),
        joinedload(Reservation.service_type)
    ).filter(Reservation.reservation_id == reservation_id).first()

    if not db_reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")

    if db_reservation.status == 'completed':
        raise HTTPException(status_code=400, detail="이미 완료된 예약입니다")

    if db_reservation.status == 'cancelled':
        raise HTTPException(status_code=400, detail="취소된 예약은 완료할 수 없습니다")

    # 1. 예약 상태를 완료로 변경
    db_reservation.status = 'completed'
    db_reservation.updated_at = datetime.utcnow()

    # 1-1. 고객의 마지막 방문일 업데이트
    customer = db_reservation.customer
    if customer:
        customer.last_visit_date = db_reservation.reservation_date
        customer.total_visits = (customer.total_visits or 0) + 1
        # 고객 상태 자동 업데이트
        customer.update_customer_status()

    # 2. 서비스 이용 기록 자동 생성
    service_usage = ServiceUsage(
        customer_id=db_reservation.customer_id,
        service_date=db_reservation.reservation_date,
        service_type_id=db_reservation.service_type_id,
        package_id=package_id,
        session_details=session_details or f"예약 #{reservation_id}에서 자동 생성",
        session_number=None,  # 패키지 사용 시 계산됨
        created_by=current_user.name
        # reservation_id는 ServiceUsage 모델에 없으므로 제거
    )

    # 3. 패키지 사용 처리
    if package_id:
        package_purchase = db.query(PackagePurchase).filter(
            PackagePurchase.purchase_id == package_id,
            PackagePurchase.customer_id == db_reservation.customer_id
        ).first()

        if not package_purchase:
            raise HTTPException(status_code=404, detail="선택한 패키지를 찾을 수 없습니다")

        if package_purchase.remaining_sessions <= 0:
            raise HTTPException(status_code=400, detail="패키지 잔여 횟수가 부족합니다")

        # 패키지 차감
        package_purchase.remaining_sessions -= 1
        package_purchase.updated_at = datetime.utcnow()

        # 세션 번호 계산 (해당 패키지의 총 사용 횟수)
        total_sessions = db.query(ServiceUsage).filter(
            ServiceUsage.package_id == package_id
        ).count()
        service_usage.session_number = total_sessions + 1

    db.add(service_usage)
    db.commit()
    db.refresh(service_usage)

    return {
        "message": "예약이 완료되었습니다",
        "service_usage_id": service_usage.usage_id,
        "package_remaining": package_purchase.remaining_sessions if package_id else None
    }
