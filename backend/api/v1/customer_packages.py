from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from typing import List, Optional, Dict
from datetime import date, datetime
from pydantic import BaseModel
import json

from core.database import get_db
from models.package import PackagePurchase, Package
from models.customer import Customer
from models.service import ServiceUsage
from schemas.response import success_response

router = APIRouter()

# redirect_slashes=False 때문에 두 버전 모두 등록
@router.get("/{customer_id}/packages", include_in_schema=False)
@router.get("/{customer_id}/packages/")
def get_customer_packages(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """고객의 패키지 구매 및 이용 현황 조회"""

    # 고객 확인
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="고객을 찾을 수 없습니다")

    # 패키지 구매 내역 조회
    purchases = db.query(PackagePurchase).filter(
        PackagePurchase.customer_id == customer_id
    ).order_by(PackagePurchase.purchase_date.desc()).all()

    result = []
    for purchase in purchases:
        # 패키지 정보 조회
        package = db.query(Package).filter(
            Package.package_id == purchase.package_id
        ).first()

        # 서비스별 이용 현황 계산
        service_usage_stats = calculate_service_usage(db, customer_id, purchase.purchase_id)

        result.append({
            "purchase_id": purchase.purchase_id,
            "package_name": package.package_name if package else "Unknown",
            "purchase_date": purchase.purchase_date.isoformat(),
            "expiry_date": purchase.expiry_date.isoformat() if purchase.expiry_date else None,
            "total_sessions": purchase.total_sessions,
            "used_sessions": purchase.used_sessions or 0,
            "remaining_sessions": purchase.remaining_sessions or purchase.total_sessions,
            "is_active": purchase.expiry_date >= date.today() if purchase.expiry_date else True,
            "service_usage": service_usage_stats
        })

    return success_response(data=result)


def calculate_service_usage(db: Session, customer_id: int, package_purchase_id: int) -> Dict[str, Dict[str, int]]:
    """패키지별 서비스 타입별 이용 현황 계산"""

    # 서비스 타입 ID 매핑
    service_type_map = {
        1: "브레인",
        2: "펄스",
        3: "림프",
        4: "레드"
    }

    # 패키지 구매 정보 조회
    purchase = db.query(PackagePurchase).filter(
        PackagePurchase.purchase_id == package_purchase_id
    ).first()

    if not purchase:
        return {}

    # 패키지 정보 조회
    package = db.query(Package).filter(
        Package.package_id == purchase.package_id
    ).first()

    # notes 필드에서 service_allocations 정보 확인
    if purchase.notes:
        try:
            notes_data = json.loads(purchase.notes)
            if 'service_allocations' in notes_data:
                usage_stats = {}
                for service_name, allocation in notes_data['service_allocations'].items():
                    total = allocation.get('total', 0)
                    used = allocation.get('used', 0)
                    usage_stats[service_name] = {
                        "total": total,
                        "used": used,
                        "remaining": total - used
                    }
                return usage_stats
        except:
            pass

    # 할당된 서비스가 없으면 기존 로직 사용 (하위 호환성)
    service_usage_counts = db.query(
        ServiceUsage.service_type_id,
        func.count(ServiceUsage.usage_id).label('count')
    ).filter(
        ServiceUsage.customer_id == customer_id,
        ServiceUsage.package_id == purchase.package_id if hasattr(ServiceUsage, 'package_id') else True
    ).group_by(ServiceUsage.service_type_id).all()

    usage_count_dict = {item[0]: item[1] for item in service_usage_counts}

    # 패키지 이름에서 서비스별 할당량 추출 시도
    usage_stats = {}

    # 통합 패키지인 경우
    if '통합' in package.package_name:
        # 전체 세션을 사용 가능한 서비스 수로 나눔
        available_services = []
        for service_name in ["브레인", "펄스", "림프", "레드"]:
            if service_name in package.package_name or '통합' in package.package_name:
                available_services.append(service_name)

        if not available_services:
            available_services = ["브레인", "펄스", "림프", "레드"]

        sessions_per_service = purchase.total_sessions // len(available_services)

        for service_id, service_name in service_type_map.items():
            if service_name in available_services:
                used_count = usage_count_dict.get(service_id, 0)
                usage_stats[service_name] = {
                    "total": sessions_per_service,
                    "used": used_count,
                    "remaining": max(0, sessions_per_service - used_count)
                }
    else:
        # 개별 패키지인 경우
        main_service = None
        for service_name in ["브레인", "펄스", "림프", "레드"]:
            if service_name in package.package_name:
                main_service = service_name
                break

        if main_service:
            # 주 서비스만 표시
            for service_id, service_name in service_type_map.items():
                if service_name == main_service:
                    used_count = usage_count_dict.get(service_id, 0)
                    usage_stats[service_name] = {
                        "total": purchase.total_sessions,
                        "used": used_count,
                        "remaining": purchase.remaining_sessions
                    }
        else:
            # 기본값: 모든 서비스 균등 분배
            sessions_per_service = purchase.total_sessions // 4
            for service_id, service_name in service_type_map.items():
                used_count = usage_count_dict.get(service_id, 0)
                usage_stats[service_name] = {
                    "total": sessions_per_service,
                    "used": used_count,
                    "remaining": max(0, sessions_per_service - used_count)
                }

    return usage_stats


@router.post("/{customer_id}/packages/{purchase_id}/use", include_in_schema=False)
@router.post("/{customer_id}/packages/{purchase_id}/use/")
def use_package_session(
    customer_id: int,
    purchase_id: int,
    service_type: str = Query(..., description="서비스 타입 (브레인, 펄스, 림프, 레드)"),
    session_details: Optional[str] = Query(None, description="세션 상세 정보"),
    db: Session = Depends(get_db)
):
    """패키지 세션 사용 기록"""

    # 패키지 구매 확인
    purchase = db.query(PackagePurchase).filter(
        and_(
            PackagePurchase.purchase_id == purchase_id,
            PackagePurchase.customer_id == customer_id
        )
    ).first()

    if not purchase:
        raise HTTPException(status_code=404, detail="패키지 구매 내역을 찾을 수 없습니다")

    # 잔여 세션 확인
    if purchase.remaining_sessions <= 0:
        raise HTTPException(status_code=400, detail="사용 가능한 세션이 없습니다")

    # 서비스 타입에 따른 service_type_id 매핑
    service_type_map = {
        "브레인": 1,
        "펄스": 2,
        "림프": 3,
        "레드": 4
    }

    service_type_id = service_type_map.get(service_type, 1)

    # 서비스 이용 기록 생성
    service_usage = ServiceUsage(
        customer_id=customer_id,
        service_date=date.today(),
        service_type_id=service_type_id,  # 중요: 서비스 타입 ID 설정
        session_details=f"{service_type}: {session_details}" if session_details else service_type,
        created_by="system"
    )

    # 패키지 사용 정보 업데이트
    purchase.used_sessions = (purchase.used_sessions or 0) + 1
    purchase.remaining_sessions = purchase.total_sessions - purchase.used_sessions

    # notes 필드의 service_allocations 업데이트
    if purchase.notes:
        try:
            notes_data = json.loads(purchase.notes)
            if 'service_allocations' in notes_data and service_type in notes_data['service_allocations']:
                notes_data['service_allocations'][service_type]['used'] = \
                    notes_data['service_allocations'][service_type].get('used', 0) + 1
                purchase.notes = json.dumps(notes_data, ensure_ascii=False)
        except:
            pass

    db.add(service_usage)
    db.commit()

    return success_response(data={
        "message": "세션이 성공적으로 사용되었습니다",
        "used_sessions": purchase.used_sessions,
        "remaining_sessions": purchase.remaining_sessions
    })


@router.get("/{customer_id}/service-history", include_in_schema=False)
@router.get("/{customer_id}/service-history/")
def get_customer_service_history(
    customer_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """고객의 서비스 이용 내역 조회"""

    # 서비스 이용 내역 조회
    query = db.query(ServiceUsage).filter(
        ServiceUsage.customer_id == customer_id
    ).order_by(ServiceUsage.service_date.desc())

    total = query.count()
    services = query.offset(skip).limit(limit).all()

    result = []
    for service in services:
        result.append({
            "usage_id": service.usage_id,
            "service_date": service.service_date.isoformat(),
            "session_details": service.session_details,
            "session_number": service.session_number,
            "created_by": service.created_by
        })

    return success_response(
        data=result,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit
    )


class UpdatePackageRequest(BaseModel):
    """패키지 잔여횟수 수정 요청"""
    used_sessions: int
    remaining_sessions: int
    notes: Optional[str] = None


class UpdateServiceAllocationRequest(BaseModel):
    """서비스별 할당량 수정 요청"""
    service_allocations: Dict[str, Dict[str, int]]  # {"브레인": {"used": 5, "total": 20}, ...}


@router.put("/{customer_id}/packages/{purchase_id}", include_in_schema=False)
@router.put("/{customer_id}/packages/{purchase_id}/")
def update_package_sessions(
    customer_id: int,
    purchase_id: int,
    request: UpdatePackageRequest,
    db: Session = Depends(get_db)
):
    """패키지 잔여횟수 수정"""

    # 패키지 구매 확인
    purchase = db.query(PackagePurchase).filter(
        and_(
            PackagePurchase.purchase_id == purchase_id,
            PackagePurchase.customer_id == customer_id
        )
    ).first()

    if not purchase:
        raise HTTPException(status_code=404, detail="패키지 구매 내역을 찾을 수 없습니다")

    # 유효성 검사
    if request.used_sessions < 0 or request.remaining_sessions < 0:
        raise HTTPException(status_code=400, detail="사용횟수와 잔여횟수는 0 이상이어야 합니다")

    # 전체 세션 수 계산
    total_sessions = request.used_sessions + request.remaining_sessions

    # 업데이트
    purchase.used_sessions = request.used_sessions
    purchase.remaining_sessions = request.remaining_sessions
    purchase.total_sessions = total_sessions

    if request.notes:
        purchase.notes = request.notes

    db.commit()

    return success_response(data={
        "message": "패키지 정보가 성공적으로 수정되었습니다",
        "purchase_id": purchase_id,
        "total_sessions": total_sessions,
        "used_sessions": request.used_sessions,
        "remaining_sessions": request.remaining_sessions
    })


@router.put("/{customer_id}/packages/{purchase_id}/services", include_in_schema=False)
@router.put("/{customer_id}/packages/{purchase_id}/services/")
def update_service_allocations(
    customer_id: int,
    purchase_id: int,
    request: UpdateServiceAllocationRequest,
    db: Session = Depends(get_db)
):
    """서비스별 할당량 수정"""

    # 패키지 구매 확인
    purchase = db.query(PackagePurchase).filter(
        and_(
            PackagePurchase.purchase_id == purchase_id,
            PackagePurchase.customer_id == customer_id
        )
    ).first()

    if not purchase:
        raise HTTPException(status_code=404, detail="패키지 구매 내역을 찾을 수 없습니다")

    # 서비스 타입 매핑
    service_type_map = {
        "브레인": 1,
        "펄스": 2,
        "림프": 3,
        "레드": 4
    }

    total_sessions = 0
    total_used = 0

    # 각 서비스별 할당량 업데이트
    for service_name, allocation in request.service_allocations.items():
        service_type_id = service_type_map.get(service_name)
        if not service_type_id:
            continue

        used = allocation.get('used', 0)
        total = allocation.get('total', 0)

        if used < 0 or total < 0 or used > total:
            raise HTTPException(
                status_code=400,
                detail=f"{service_name}: 유효하지 않은 값입니다"
            )

        total_sessions += total
        total_used += used

        # 서비스 할당 정보를 메타데이터로 저장 (실제로는 별도 테이블이 필요)
        # 임시로 notes에 JSON으로 저장
        if purchase.notes:
            try:
                notes_data = json.loads(purchase.notes)
            except:
                notes_data = {}
        else:
            notes_data = {}

        if 'service_allocations' not in notes_data:
            notes_data['service_allocations'] = {}

        notes_data['service_allocations'][service_name] = {
            'total': total,
            'used': used
        }

        purchase.notes = json.dumps(notes_data, ensure_ascii=False)

    # 전체 세션 정보 업데이트
    purchase.total_sessions = total_sessions
    purchase.used_sessions = total_used
    purchase.remaining_sessions = total_sessions - total_used

    db.commit()

    return success_response(data={
        "message": "서비스별 할당량이 수정되었습니다",
        "purchase_id": purchase_id,
        "total_sessions": total_sessions,
        "used_sessions": total_used,
        "remaining_sessions": total_sessions - total_used,
        "service_allocations": request.service_allocations
    })
