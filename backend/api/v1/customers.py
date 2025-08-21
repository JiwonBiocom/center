from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, or_, and_, text
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import pandas as pd
import io

from core.database import get_db
from models.customer import Customer as CustomerModel
from schemas.customer import Customer, CustomerCreate, CustomerUpdate
from utils.excel import ExcelHandler, ExcelValidator
from utils.error_handlers import ErrorResponses, handle_database_error, handle_api_errors
from crud.customer import customer as customer_crud
from schemas.response import APIResponse, PaginatedResponse, success_response, paginated_response
from utils.response_wrapper import wrap_response, wrap_paginated_response

router = APIRouter()

# redirect_slashes=False 때문에 두 버전 모두 등록
@router.post("", response_model=Customer, include_in_schema=False)
@router.post("/", response_model=Customer)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """새로운 고객 생성"""
    return customer_crud.create_with_duplicate_check(db, obj_in=customer)

@router.get("", response_model=PaginatedResponse[Customer], include_in_schema=False)
@router.get("/", response_model=PaginatedResponse[Customer])
def read_customers(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    # 기본 필터
    region: Optional[str] = None,
    referral_source: Optional[str] = None,
    assigned_staff: Optional[str] = None,
    # 고급 필터
    membership_level: Optional[str] = None,
    customer_status: Optional[str] = None,
    # 날짜 범위
    first_visit_from: Optional[date] = None,
    first_visit_to: Optional[date] = None,
    # 정렬
    sort_by: Optional[str] = Query(None, description="정렬 기준: last_visit_date, name, membership_level, assigned_staff"),
    sort_order: Optional[str] = Query("desc", description="정렬 순서: asc, desc"),
    db: Session = Depends(get_db)
):
    """고객 목록 조회 (페이지네이션 지원)"""
    try:
        # 기본 쿼리
        query = select(CustomerModel)

        # 검색 조건 적용
        if search:
            search_conditions = [
                CustomerModel.name.contains(search),
                CustomerModel.phone.contains(search)
            ]
            # email이 None이 아닌 경우에만 검색
            if search:
                search_conditions.append(
                    and_(CustomerModel.email.is_not(None), CustomerModel.email.contains(search))
                )
            query = query.where(or_(*search_conditions))

        # 기본 필터
        if region:
            query = query.where(CustomerModel.region.ilike(f"%{region}%"))

        if referral_source:
            query = query.where(CustomerModel.referral_source == referral_source)

        if assigned_staff:
            query = query.where(CustomerModel.assigned_staff == assigned_staff)

        # 고급 필터
        if membership_level:
            query = query.where(CustomerModel.membership_level == membership_level)

        if customer_status:
            query = query.where(CustomerModel.customer_status == customer_status)

        # 날짜 필터
        if first_visit_from:
            query = query.where(CustomerModel.first_visit_date >= first_visit_from)
        if first_visit_to:
            query = query.where(CustomerModel.first_visit_date <= first_visit_to)

        # 정렬
        if sort_by == "last_visit_date":
            if sort_order == "asc":
                query = query.order_by(CustomerModel.last_visit_date.asc().nulls_last())
            else:
                query = query.order_by(CustomerModel.last_visit_date.desc().nulls_last())
        elif sort_by == "name":
            if sort_order == "asc":
                query = query.order_by(CustomerModel.name.asc())
            else:
                query = query.order_by(CustomerModel.name.desc())
        elif sort_by == "membership_level":
            if sort_order == "asc":
                query = query.order_by(CustomerModel.membership_level.asc())
            else:
                query = query.order_by(CustomerModel.membership_level.desc())
        elif sort_by == "assigned_staff":
            if sort_order == "asc":
                query = query.order_by(CustomerModel.assigned_staff.asc().nulls_last())
            else:
                query = query.order_by(CustomerModel.assigned_staff.desc().nulls_last())
        elif sort_by == "created_at":
            if sort_order == "asc":
                query = query.order_by(CustomerModel.created_at.asc())
            else:
                query = query.order_by(CustomerModel.created_at.desc())
        else:
            # 기본 정렬 - 최신 등록 고객부터
            query = query.order_by(CustomerModel.created_at.desc())

        # 전체 개수 조회
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar()

        # 페이지네이션 적용
        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        customers = result.scalars().all()

        # skip과 limit를 page와 page_size로 변환
        page = (skip // limit) + 1 if limit > 0 else 1

        # SQLAlchemy 모델을 Pydantic 스키마로 변환
        print(f"DEBUG: 조회된 고객 수: {len(customers)}")
        print(f"DEBUG: 전체 고객 수: {total}")

        customer_schemas = []
        for customer in customers:
            try:
                schema = Customer.model_validate(customer)
                customer_schemas.append(schema)
            except Exception as e:
                print(f"DEBUG: Customer 변환 에러 - ID {customer.customer_id}: {e}")

        print(f"DEBUG: 변환된 스키마 수: {len(customer_schemas)}")

        return paginated_response(
            data=customer_schemas,
            total=total,
            page=page,
            page_size=limit
        )
    except Exception as e:
        print(f"고객 조회 에러 상세: {str(e)}")
        print(f"에러 타입: {type(e)}")
        # 에러 발생 시에도 페이지네이션 응답 반환
        page = (skip // limit) + 1 if limit > 0 else 1

        return paginated_response(
            data=[],
            total=0,
            page=page,
            page_size=limit
        )

@router.get("/regions/autocomplete")
def get_regions_autocomplete(
    q: Optional[str] = Query(None, description="검색어"),
    limit: int = Query(10, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """지역 자동완성"""
    query = select(CustomerModel.region).distinct()

    if q:
        query = query.where(CustomerModel.region.ilike(f"%{q}%"))

    query = query.where(CustomerModel.region.is_not(None)).order_by(CustomerModel.region).limit(limit)

    result = db.execute(query)
    regions = [row[0] for row in result.all() if row[0]]

    return {"regions": regions}

@router.get("/referral-sources")
def get_referral_sources(
    db: Session = Depends(get_db)
):
    """유입경로 목록 조회"""
    query = select(CustomerModel.referral_source).distinct()
    query = query.where(CustomerModel.referral_source.is_not(None)).order_by(CustomerModel.referral_source)

    result = db.execute(query)
    sources = [row[0] for row in result.all() if row[0]]

    return {"referral_sources": sources}

@router.get("/count")
def count_customers(
    search: Optional[str] = None,
    # 기본 필터
    region: Optional[str] = None,
    referral_source: Optional[str] = None,
    # 고급 필터
    membership_level: Optional[str] = None,
    customer_status: Optional[str] = None,
    # 나이 범위
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    # 매출 범위 (만원)
    revenue_min: Optional[float] = None,
    revenue_max: Optional[float] = None,
    # 방문 횟수 범위
    visits_min: Optional[int] = None,
    visits_max: Optional[int] = None,
    # 날짜 범위
    first_visit_from: Optional[date] = None,
    first_visit_to: Optional[date] = None,
    last_visit_from: Optional[date] = None,
    last_visit_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """고객 수 조회 (고급 필터링 지원)"""
    query = select(func.count(CustomerModel.customer_id))

    # 기본 검색 필터
    if search:
        search_conditions = [
            CustomerModel.name.contains(search),
            CustomerModel.phone.contains(search),
            and_(CustomerModel.email.is_not(None), CustomerModel.email.contains(search))
        ]
        query = query.where(or_(*search_conditions))

    # 기본 필터
    if region:
        query = query.where(CustomerModel.region.ilike(f"%{region}%"))

    if referral_source:
        query = query.where(CustomerModel.referral_source == referral_source)

    # 고급 필터
    if membership_level:
        query = query.where(CustomerModel.membership_level == membership_level)

    if customer_status:
        query = query.where(CustomerModel.customer_status == customer_status)

    # 나이 범위 필터 (현재 연도 기준)
    if age_min is not None or age_max is not None:
        current_year = datetime.now().year
        if age_min is not None:
            max_birth_year = current_year - age_min
            query = query.where(CustomerModel.birth_year <= max_birth_year)
        if age_max is not None:
            min_birth_year = current_year - age_max
            query = query.where(CustomerModel.birth_year >= min_birth_year)

    # 매출 범위 필터 (만원 단위)
    if revenue_min is not None:
        query = query.where(CustomerModel.total_revenue >= revenue_min * 10000)
    if revenue_max is not None:
        query = query.where(CustomerModel.total_revenue <= revenue_max * 10000)

    # 방문 횟수 범위 필터
    if visits_min is not None:
        query = query.where(CustomerModel.total_visits >= visits_min)
    if visits_max is not None:
        query = query.where(CustomerModel.total_visits <= visits_max)

    # 첫 방문일 범위 필터
    if first_visit_from:
        query = query.where(CustomerModel.first_visit_date >= first_visit_from)
    if first_visit_to:
        query = query.where(CustomerModel.first_visit_date <= first_visit_to)

    # 마지막 방문일 범위 필터
    if last_visit_from:
        query = query.where(CustomerModel.last_visit_date >= last_visit_from)
    if last_visit_to:
        query = query.where(CustomerModel.last_visit_date <= last_visit_to)

    result = db.execute(query)
    count = result.scalar()
    return {"count": count}

@router.get("/{customer_id}", response_model=Customer, include_in_schema=False)
@router.get("/{customer_id}/", response_model=Customer)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """특정 고객 조회"""
    stmt = select(CustomerModel).where(CustomerModel.customer_id == customer_id)
    result = db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise ErrorResponses.not_found("고객", customer_id)

    return customer

@router.get("/{customer_id}/detail", include_in_schema=False)
@router.get("/{customer_id}/detail/")
def read_customer_detail(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """고객 상세 정보 조회 (프론트엔드 호환용)"""
    stmt = select(CustomerModel).where(CustomerModel.customer_id == customer_id)
    result = db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise ErrorResponses.not_found("고객", customer_id)

    # 프론트엔드가 기대하는 형태로 응답
    customer_schema = Customer.model_validate(customer)

    # risk_level 필드 추가 (임시)
    customer_dict = customer_schema.model_dump()
    customer_dict['risk_level'] = 'stable'  # 기본값
    
    # InBody 기록 추가
    from models.inbody import InBodyRecord
    inbody_records = db.query(InBodyRecord).filter(
        InBodyRecord.customer_id == customer_id
    ).order_by(InBodyRecord.measurement_date.desc()).all()
    
    inbody_list = []
    for record in inbody_records:
        inbody_list.append({
            "record_id": record.record_id,
            "customer_id": record.customer_id,
            "measurement_date": record.measurement_date.isoformat() if record.measurement_date else None,
            "weight": record.weight,
            "body_fat_percentage": record.body_fat_percentage,
            "skeletal_muscle_mass": record.skeletal_muscle_mass,
            "extracellular_water_ratio": record.extracellular_water_ratio,
            "phase_angle": record.phase_angle,
            "visceral_fat_level": record.visceral_fat_level,
            "notes": record.notes,
            "measured_by": record.measured_by,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None
        })

    return {
        "customer": customer_dict,
        "inbodyRecords": inbody_list
    }

@router.put("/{customer_id}", response_model=Customer, include_in_schema=False)
@router.put("/{customer_id}/", response_model=Customer)
@router.patch("/{customer_id}", response_model=Customer, include_in_schema=False)
@router.patch("/{customer_id}/", response_model=Customer)
@handle_database_error
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """고객 정보 수정"""
    stmt = select(CustomerModel).where(CustomerModel.customer_id == customer_id)
    result = db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise ErrorResponses.not_found("고객", customer_id)

    # 전화번호 중복 체크 (다른 고객과 중복되는 경우)
    if customer_update.phone and customer_update.phone != customer.phone:
        stmt = select(CustomerModel).where(
            (CustomerModel.phone == customer_update.phone) &
            (CustomerModel.customer_id != customer_id)
        )
        result = db.execute(stmt)
        if result.scalar_one_or_none():
            raise ErrorResponses.already_exists("고객", "전화번호", customer_update.phone)

    # 업데이트
    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}", include_in_schema=False)
@router.delete("/{customer_id}/")
@handle_database_error
def delete_customer(
    customer_id: int,
    cascade: bool = Query(False, description="관련 데이터도 함께 삭제"),
    db: Session = Depends(get_db)
):
    """고객 삭제"""
    stmt = select(CustomerModel).where(CustomerModel.customer_id == customer_id)
    result = db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise ErrorResponses.not_found("고객", customer_id)

    if cascade:
        # 관련 데이터 먼저 삭제
        from models.payment import Payment
        from models.service import ServiceUsage
        from models.reservation import Reservation
        from models.customer_extended import KitReceipt

        # 서비스 이용 내역 삭제
        db.execute(text("DELETE FROM service_usage WHERE customer_id = :id"), {"id": customer_id})

        # 결제 내역 삭제
        db.execute(text("DELETE FROM payments WHERE customer_id = :id"), {"id": customer_id})

        # 예약 삭제
        db.execute(text("DELETE FROM reservations WHERE customer_id = :id"), {"id": customer_id})

        # 키트 수령 삭제
        db.execute(text("DELETE FROM kit_receipts WHERE customer_id = :id"), {"id": customer_id})

    db.delete(customer)
    db.commit()
    return {"message": "고객이 삭제되었습니다."}

@router.get("/stats/by-region")
def customer_stats_by_region(
    db: Session = Depends(get_db)
):
    """지역별 고객 통계"""
    query = select(
        CustomerModel.region,
        func.count(CustomerModel.customer_id).label('count')
    ).group_by(CustomerModel.region).order_by(func.count(CustomerModel.customer_id).desc())

    result = db.execute(query)
    stats = result.all()

    return [{"region": stat[0] or "미지정", "count": stat[1]} for stat in stats]

@router.get("/stats/by-referral")
def customer_stats_by_referral(
    db: Session = Depends(get_db)
):
    """유입경로별 고객 통계"""
    query = select(
        CustomerModel.referral_source,
        func.count(CustomerModel.customer_id).label('count')
    ).group_by(CustomerModel.referral_source).order_by(func.count(CustomerModel.customer_id).desc())

    result = db.execute(query)
    stats = result.all()

    return [{"referral_source": stat[0] or "미지정", "count": stat[1]} for stat in stats]

@router.post("/import/excel", include_in_schema=False)
@router.post("/import/excel/")
async def import_customers_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """엑셀 파일에서 고객 데이터 가져오기"""
    # 특정 시트가 있는 경우 처리
    if hasattr(file, 'filename') and file.filename and '고객관리대장' in file.filename:
        # 고객관리대장 형식의 경우 특별 처리
        try:
            contents = await file.read()
            xl_file = pd.ExcelFile(io.BytesIO(contents))

            # '전체 고객관리대장' 시트 찾기
            if '전체 고객관리대장' in xl_file.sheet_names:
                df = pd.read_excel(xl_file, sheet_name='전체 고객관리대장', header=2)
                # NO 컬럼이 있는 행만 필터링 (실제 데이터)
                if 'NO' in df.columns:
                    df = df.dropna(subset=['NO'])
            else:
                # 기본 시트 읽기
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            print(f"고객관리대장 특별 처리 실패: {e}")
            # 실패 시 일반 처리
            await file.seek(0)
            df = await ExcelHandler.read_excel_file(file)
    else:
        # 일반 엑셀 파일 읽기
        df = await ExcelHandler.read_excel_file(file)

    # 컬럼명 매핑 (다양한 형식 지원)
    column_mapping = {
        '성함': '이름',
        '연락처': '전화번호',
        '거주지역': '지역',
        '방문경로': '유입경로',
        '비고(메모)': '메모',
        '담당자': '담당직원',
        '첫방문일': '첫방문일자',
        '첫 방문일': '첫방문일자',  # 띄어쓰기 있는 버전
        '첫방문일자': '첫방문일자',  # 이미 정확한 경우
        '최초방문일': '첫방문일자',  # 다른 표현
        '최초 방문일': '첫방문일자',
        '첫방문': '첫방문일자',
        '등록일': '첫방문일자',  # 등록일도 첫방문일로 매핑
        '가입일': '첫방문일자',  # 가입일도 지원
        '호소문제': '건강고민'
    }

    # 컬럼명 변경
    df = df.rename(columns=column_mapping)

    # 디버깅: 엑셀 컬럼명 확인
    print(f"엑셀 파일 컬럼: {list(df.columns)}")
    print(f"첫방문일자 컬럼 존재 여부: {'첫방문일자' in df.columns}")
    print(f"등록일 컬럼 존재 여부: {'등록일' in df.columns}")
    
    if '첫방문일자' in df.columns:
        print(f"첫방문일자 샘플 데이터 (처음 5개): {df['첫방문일자'].head().tolist()}")
    elif '등록일' in df.columns:
        print(f"등록일 샘플 데이터 (처음 5개): {df['등록일'].head().tolist()}")

    # 필수 컬럼 검증
    required_columns = ['이름', '전화번호']
    # 유연한 검증 - 매핑된 컬럼명도 확인
    missing_columns = []
    for req_col in required_columns:
        if req_col not in df.columns:
            # 매핑 전 컬럼명도 확인
            found = False
            for old_col, new_col in column_mapping.items():
                if new_col == req_col and old_col in df.columns:
                    found = True
                    break
            if not found:
                missing_columns.append(req_col)

    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
        )

    # 엑셀 파일 내 중복 체크 (NaN 제외)
    df_with_phone = df[df['전화번호'].notna()]
    phone_counts = df_with_phone['전화번호'].value_counts()
    excel_duplicates = phone_counts[phone_counts > 1]

    # 중복된 전화번호가 있으면 경고만 표시 (에러로 중단하지 않음)
    duplicate_warning = []
    if len(excel_duplicates) > 0:
        duplicate_warning.append(f"엑셀 파일 내 중복된 전화번호 {len(excel_duplicates)}개 발견")

    # 데이터 처리 결과
    success_count = 0
    error_count = 0
    errors = []
    first_visit_date_issues = 0  # 첫방문일 파싱 실패 수

    total_rows = len(df)
    print(f"총 {total_rows}개 행 처리 시작...")

    for index, row in df.iterrows():
        # 진행 상황 출력 (10행마다)
        if index > 0 and index % 10 == 0:
            print(f"진행 중... {index}/{total_rows} ({index/total_rows*100:.1f}%)")
        try:
            # 데이터 정제 - 첫방문일자 또는 등록일 컬럼 사용
            first_visit_raw = row.get('첫방문일자') or row.get('등록일')
            first_visit_parsed = ExcelHandler.parse_date(first_visit_raw)

            # 디버깅 로그 (첫방문일 파싱 확인)
            if index < 5:  # 처음 5행만 상세 로그
                print(f"행 {index + 2} 첫방문일 처리:")
                print(f"  - 원본값: {first_visit_raw}")
                print(f"  - 타입: {type(first_visit_raw)}")
                print(f"  - 파싱 결과: {first_visit_parsed}")

            if first_visit_raw and not first_visit_parsed:
                print(f"첫방문일 파싱 실패 - 행 {index + 2}: 원본값={first_visit_raw}, 타입={type(first_visit_raw)}")
                first_visit_date_issues += 1

            customer_data = {
                'name': ExcelHandler.clean_string(row.get('이름')),
                'phone': ExcelHandler.clean_phone(row.get('전화번호')),
                'email': ExcelHandler.clean_string(row.get('이메일')),
                'birth_year': ExcelHandler.parse_year(row.get('생년월일')),
                'gender': ExcelHandler.clean_string(row.get('성별')),
                'address': ExcelHandler.clean_string(row.get('주소')),
                'region': ExcelHandler.clean_string(row.get('지역')),
                'referral_source': ExcelHandler.clean_string(row.get('유입경로')),
                'notes': ExcelHandler.clean_string(row.get('메모')),
                'health_concerns': ExcelHandler.clean_string(row.get('건강고민')),
                'assigned_staff': ExcelHandler.clean_string(row.get('담당직원')),
                'first_visit_date': first_visit_parsed
            }

            # None 값 제거
            customer_data = {k: v for k, v in customer_data.items() if v is not None}

            # enum 타입 필드는 제외 (모델의 기본값 사용)
            customer_data.pop('membership_level', None)
            customer_data.pop('customer_status', None)

            # 필수 데이터 검증
            if not customer_data.get('name'):
                error_count += 1
                errors.append(f"행 {index + 2}: 이름이 없습니다")
                continue

            # 중복 전화번호 체크 (전화번호가 있는 경우만)
            if customer_data.get('phone'):
                existing = db.query(CustomerModel).filter(
                    CustomerModel.phone == customer_data['phone']
                ).first()
                if existing:
                    error_count += 1
                    errors.append(f"행 {index + 2}: 전화번호 {customer_data['phone']}는 이미 등록됨 (고객: {existing.name})")
                    continue

            # 고객 생성 (한 번에 하나씩 커밋)
            try:
                db_customer = CustomerModel(**customer_data)
                db.add(db_customer)
                db.commit()
                db.refresh(db_customer)

                # 디버깅: 실제 저장된 값 확인
                if index < 5:
                    print(f"DB 저장 완료 - 고객 ID: {db_customer.customer_id}")
                    print(f"  - 이름: {db_customer.name}")
                    print(f"  - 첫방문일: {db_customer.first_visit_date}")

                success_count += 1
            except Exception as e:
                db.rollback()
                error_count += 1
                errors.append(f"행 {index + 2}: 데이터베이스 저장 실패 - {str(e)}")
                continue

        except Exception as e:
            error_count += 1
            errors.append(f"행 {index + 2}: {str(e)}")

    # 이미 개별적으로 커밋했으므로 추가 커밋 불필요

    result = {
        "message": f"엑셀 가져오기 완료",
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors[:10]  # 최대 10개 에러만 반환
    }

    # 경고 메시지 추가
    if duplicate_warning:
        result["warnings"] = duplicate_warning

    # 첫방문일 관련 정보 추가
    if first_visit_date_issues > 0:
        result["first_visit_date_issues"] = True
        result["warnings"] = result.get("warnings", [])
        result["warnings"].append(f"첫방문일 파싱 실패: {first_visit_date_issues}건")

    print(f"\n처리 완료 - 성공: {success_count}, 실패: {error_count}, 첫방문일 문제: {first_visit_date_issues}")

    return result

@router.get("/export/excel")
def export_customers_to_excel(
    search: Optional[str] = None,
    region: Optional[str] = None,
    referral_source: Optional[str] = None,
    membership_level: Optional[str] = None,
    customer_status: Optional[str] = None,
    risk_level: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    revenue_min: Optional[float] = None,
    revenue_max: Optional[float] = None,
    visits_min: Optional[int] = None,
    visits_max: Optional[int] = None,
    first_visit_from: Optional[date] = None,
    first_visit_to: Optional[date] = None,
    last_visit_from: Optional[date] = None,
    last_visit_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """고객 데이터를 엑셀 파일로 내보내기 - 필터링 지원"""
    # 고객 조회 (fetchCustomers와 동일한 필터 적용)
    query = select(CustomerModel)

    # 검색어 필터
    if search:
        query = query.where(
            (CustomerModel.name.contains(search)) |
            (CustomerModel.phone.contains(search))
        )

    # 지역 필터
    if region:
        query = query.where(CustomerModel.region.ilike(f"%{region}%"))

    # 유입경로 필터
    if referral_source:
        query = query.where(CustomerModel.referral_source == referral_source)

    # 멤버십 레벨 필터
    if membership_level:
        query = query.where(CustomerModel.membership_level == membership_level)

    # 고객 상태 필터
    if customer_status:
        query = query.where(CustomerModel.customer_status == customer_status)

    # 위험도 필터
    if risk_level:
        query = query.where(CustomerModel.risk_level == risk_level)

    # 나이 범위 필터
    if age_min is not None or age_max is not None:
        current_year = datetime.now().year
        if age_min is not None and age_max is not None:
            query = query.where(and_(
                CustomerModel.birth_year >= current_year - age_max,
                CustomerModel.birth_year <= current_year - age_min
            ))
        elif age_min is not None:
            query = query.where(CustomerModel.birth_year <= current_year - age_min)
        elif age_max is not None:
            query = query.where(CustomerModel.birth_year >= current_year - age_max)

    # 첫 방문일 범위 필터
    if first_visit_from:
        query = query.where(CustomerModel.first_visit_date >= first_visit_from)
    if first_visit_to:
        query = query.where(CustomerModel.first_visit_date <= first_visit_to)

    # 마지막 방문일 범위 필터
    if last_visit_from:
        query = query.where(CustomerModel.last_visit_date >= last_visit_from)
    if last_visit_to:
        query = query.where(CustomerModel.last_visit_date <= last_visit_to)

    query = query.order_by(CustomerModel.customer_id.desc())

    result = db.execute(query)
    customers = result.scalars().all()

    # DataFrame 생성
    data = []
    for customer in customers:
        data.append({
            '고객ID': customer.customer_id,
            '이름': customer.name,
            '전화번호': customer.phone,
            '이메일': customer.email,
            '출생연도': customer.birth_year if customer.birth_year else '',
            '성별': customer.gender,
            '주소': customer.address,
            '지역': customer.region,
            '유입경로': customer.referral_source,
            '메모': customer.notes,
            '등록일': customer.created_at.strftime('%Y-%m-%d %H:%M:%S') if customer.created_at else ''
        })

    df = pd.DataFrame(data)

    # 엑셀 파일 생성
    excel_data = ExcelHandler.create_excel_response(
        df,
        f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    return Response(
        content=excel_data,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f'attachment; filename=customers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        }
    )
