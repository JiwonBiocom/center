from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, datetime
import pandas as pd

from core.database import get_db
from core.auth import get_current_user
from models.service import ServiceUsage as ServiceUsageModel, ServiceType as ServiceTypeModel
from models.customer import Customer as CustomerModel
from models.package import PackagePurchase as PackagePurchaseModel
from models.user import User
from schemas.service import ServiceUsage, ServiceUsageCreate, ServiceType
from utils.excel import ExcelHandler

router = APIRouter()

@router.get("/")
def get_services_info():
    """서비스 API 정보"""
    return {
        "message": "Services API",
        "available_endpoints": [
            "/types - 서비스 타입 목록",
            "/usage - 서비스 이용 내역",
            "/calendar - 서비스 이용 캘린더",
            "/export/excel - 엑셀 내보내기"
        ]
    }

@router.get("/types", response_model=List[ServiceType])
def get_service_types(db: Session = Depends(get_db)):
    """서비스 타입 목록 조회"""
    query = select(ServiceTypeModel)
    result = db.execute(query)
    return result.scalars().all()

@router.post("/usage", response_model=ServiceUsage)
def create_service_usage(
    usage: ServiceUsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서비스 이용 등록"""
    # 고객 확인
    customer_query = select(CustomerModel).where(CustomerModel.customer_id == usage.customer_id)
    customer_result = db.execute(customer_query)
    customer = customer_result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="고객을 찾을 수 없습니다.")

    # 패키지 확인 및 잔여 횟수 체크
    if usage.package_id:
        package_query = select(PackagePurchaseModel).where(
            and_(
                PackagePurchaseModel.purchase_id == usage.package_id,
                PackagePurchaseModel.customer_id == usage.customer_id
            )
        )
        package_result = db.execute(package_query)
        package = package_result.scalar_one_or_none()

        if not package:
            raise HTTPException(status_code=404, detail="패키지를 찾을 수 없습니다.")

        if package.remaining_sessions <= 0:
            raise HTTPException(status_code=400, detail="패키지 잔여 횟수가 없습니다.")

        # 패키지 차감
        package.used_sessions += 1
        package.remaining_sessions -= 1

    # 서비스 이용 기록 생성
    db_usage = ServiceUsageModel(**usage.model_dump())
    db.add(db_usage)

    db.commit()
    db.refresh(db_usage)

    return db_usage

@router.get("/usage", response_model=List[dict])
def get_service_usage(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    customer_id: Optional[int] = None,
    service_type_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서비스 이용 내역 조회"""
    query = select(
        ServiceUsageModel,
        CustomerModel.name.label('customer_name'),
        ServiceTypeModel.service_name.label('service_name')
    ).join(
        CustomerModel, ServiceUsageModel.customer_id == CustomerModel.customer_id
    ).join(
        ServiceTypeModel, ServiceUsageModel.service_type_id == ServiceTypeModel.service_type_id
    )

    # 필터링
    if date_from:
        query = query.where(ServiceUsageModel.service_date >= date_from)
    if date_to:
        query = query.where(ServiceUsageModel.service_date <= date_to)
    if customer_id:
        query = query.where(ServiceUsageModel.customer_id == customer_id)
    if service_type_id:
        query = query.where(ServiceUsageModel.service_type_id == service_type_id)

    # 정렬 및 페이지네이션
    query = query.order_by(ServiceUsageModel.service_date.desc(), ServiceUsageModel.usage_id.desc())
    query = query.offset(skip).limit(limit)

    result = db.execute(query)
    rows = result.all()

    # 결과 포맷팅
    usage_list = []
    for row in rows:
        usage = row[0]
        usage_dict = {
            "usage_id": usage.usage_id,
            "customer_id": usage.customer_id,
            "customer_name": row.customer_name,
            "service_date": usage.service_date.isoformat(),
            "service_type_id": usage.service_type_id,
            "service_name": row.service_name,
            "package_id": usage.package_id,
            "session_details": usage.session_details,
            "session_number": usage.session_number,
            "created_by": usage.created_by,
            "created_at": usage.created_at.isoformat()
        }
        usage_list.append(usage_dict)

    return usage_list

@router.get("/calendar")
def get_calendar_data(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """캘린더 데이터 조회"""
    # 해당 월의 서비스 이용 데이터 집계
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    # 날짜별 총 서비스 수와 고객 수
    query = select(
        ServiceUsageModel.service_date,
        func.count(ServiceUsageModel.usage_id).label('count'),
        func.count(func.distinct(ServiceUsageModel.customer_id)).label('unique_customers')
    ).where(
        and_(
            ServiceUsageModel.service_date >= start_date,
            ServiceUsageModel.service_date < end_date
        )
    ).group_by(ServiceUsageModel.service_date)

    result = db.execute(query)
    data = result.all()

    # 날짜별 서비스 타입별 통계
    service_query = select(
        ServiceUsageModel.service_date,
        ServiceTypeModel.service_name,
        func.count(ServiceUsageModel.usage_id).label('count')
    ).join(
        ServiceTypeModel, ServiceUsageModel.service_type_id == ServiceTypeModel.service_type_id
    ).where(
        and_(
            ServiceUsageModel.service_date >= start_date,
            ServiceUsageModel.service_date < end_date
        )
    ).group_by(ServiceUsageModel.service_date, ServiceTypeModel.service_name)

    service_result = db.execute(service_query)
    service_data = service_result.all()

    # 데이터 구조화
    calendar_data = {}

    # 기본 데이터 설정
    for row in data:
        calendar_data[row.service_date.isoformat()] = {
            "total_services": row.count,
            "unique_customers": row.unique_customers,
            "services": {}
        }

    # 서비스별 데이터 추가
    for row in service_data:
        date_str = row.service_date.isoformat()
        if date_str in calendar_data:
            calendar_data[date_str]["services"][row.service_name] = row.count

    return calendar_data

@router.get("/customer/{customer_id}/packages")
def get_customer_packages(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객의 활성 패키지 조회"""
    query = select(PackagePurchaseModel).where(
        and_(
            PackagePurchaseModel.customer_id == customer_id,
            PackagePurchaseModel.remaining_sessions > 0,
            PackagePurchaseModel.expiry_date >= date.today()
        )
    )

    result = db.execute(query)
    packages = result.scalars().all()

    return [
        {
            "purchase_id": p.purchase_id,
            "package_id": p.package_id,
            "purchase_date": p.purchase_date.isoformat(),
            "expiry_date": p.expiry_date.isoformat() if p.expiry_date else None,
            "total_sessions": p.total_sessions,
            "used_sessions": p.used_sessions,
            "remaining_sessions": p.remaining_sessions
        }
        for p in packages
    ]

@router.get("/stats")
def get_service_stats(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서비스 통계 조회"""
    # 해당 월의 시작/끝 날짜
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    # 총 서비스 수
    total_services_query = select(func.count(ServiceUsageModel.usage_id)).where(
        and_(
            ServiceUsageModel.service_date >= start_date,
            ServiceUsageModel.service_date < end_date
        )
    )
    total_services = db.execute(total_services_query).scalar() or 0

    # 고유 고객 수
    unique_customers_query = select(func.count(func.distinct(ServiceUsageModel.customer_id))).where(
        and_(
            ServiceUsageModel.service_date >= start_date,
            ServiceUsageModel.service_date < end_date
        )
    )
    unique_customers = db.execute(unique_customers_query).scalar() or 0

    # 가장 인기 있는 서비스
    popular_service_query = select(
        ServiceTypeModel.service_name,
        func.count(ServiceUsageModel.usage_id).label('count')
    ).join(
        ServiceTypeModel, ServiceUsageModel.service_type_id == ServiceTypeModel.service_type_id
    ).where(
        and_(
            ServiceUsageModel.service_date >= start_date,
            ServiceUsageModel.service_date < end_date
        )
    ).group_by(ServiceTypeModel.service_name).order_by(func.count(ServiceUsageModel.usage_id).desc()).limit(1)

    popular_service_result = db.execute(popular_service_query).first()
    most_popular_service = popular_service_result[0] if popular_service_result else "N/A"

    # 총 매출 (기본 가격 기준)
    revenue_query = select(
        func.sum(ServiceTypeModel.default_price)
    ).select_from(ServiceUsageModel).join(
        ServiceTypeModel, ServiceUsageModel.service_type_id == ServiceTypeModel.service_type_id
    ).where(
        and_(
            ServiceUsageModel.service_date >= start_date,
            ServiceUsageModel.service_date < end_date
        )
    )
    total_revenue = db.execute(revenue_query).scalar() or 0

    # 일평균 서비스 수
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    average_daily_services = total_services / days_in_month if days_in_month > 0 else 0

    return {
        "total_services": total_services,
        "unique_customers": unique_customers,
        "most_popular_service": most_popular_service,
        "total_revenue": total_revenue,
        "average_daily_services": round(average_daily_services, 1)
    }

@router.get("/usage/export/excel")
def export_service_usage_to_excel(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    customer_id: Optional[int] = None,
    service_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """서비스 이용 내역을 엑셀 파일로 내보내기"""
    # 서비스 이용 내역 조회
    query = select(
        ServiceUsageModel,
        CustomerModel.name.label('customer_name'),
        CustomerModel.phone.label('customer_phone'),
        ServiceTypeModel.service_name.label('service_name'),
        PackagePurchaseModel.package_id.label('package_name')
    ).join(
        CustomerModel, ServiceUsageModel.customer_id == CustomerModel.customer_id
    ).join(
        ServiceTypeModel, ServiceUsageModel.service_type_id == ServiceTypeModel.service_type_id
    ).outerjoin(
        PackagePurchaseModel, ServiceUsageModel.package_id == PackagePurchaseModel.purchase_id
    )

    # 필터링
    if date_from:
        query = query.where(ServiceUsageModel.service_date >= date_from)
    if date_to:
        query = query.where(ServiceUsageModel.service_date <= date_to)
    if customer_id:
        query = query.where(ServiceUsageModel.customer_id == customer_id)
    if service_type_id:
        query = query.where(ServiceUsageModel.service_type_id == service_type_id)

    # 정렬
    query = query.order_by(ServiceUsageModel.service_date.desc(), ServiceUsageModel.usage_id.desc())

    result = db.execute(query)
    rows = result.all()

    # DataFrame 생성
    data = []
    for row in rows:
        usage = row[0]
        data.append({
            '이용ID': usage.usage_id,
            '서비스일자': usage.service_date.strftime('%Y-%m-%d'),
            '고객명': row.customer_name,
            '전화번호': row.customer_phone,
            '서비스종류': row.service_name,
            '세션번호': usage.session_number or '',
            '세션내용': usage.session_details or '',
            '패키지사용': '예' if usage.package_id else '아니오',
            '담당자': usage.created_by or '',
            '등록일시': usage.created_at.strftime('%Y-%m-%d %H:%M:%S') if usage.created_at else ''
        })

    df = pd.DataFrame(data)

    # 엑셀 파일 생성
    excel_data = ExcelHandler.create_excel_response(
        df,
        f"service_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    return Response(
        content=excel_data,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f'attachment; filename=service_usage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        }
    )
