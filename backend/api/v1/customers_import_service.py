from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import pandas as pd
import io
from datetime import datetime

from core.database import get_db
from models.customer import Customer as CustomerModel
from models.service import ServiceUsage as ServiceUsageModel
from models.package import PackagePurchase as PackagePurchaseModel
from utils.excel import ExcelHandler

router = APIRouter()

@router.post("/import/service-history")
@router.post("/import/service-history/")
async def import_service_history(
    file: UploadFile = File(...),
    update_mode: Optional[str] = Query("merge", description="업데이트 모드: merge(병합), replace(교체)"),
    db: Session = Depends(get_db)
):
    """
    엑셀 파일에서 서비스 이력 데이터 가져오기
    - 고객번호 또는 이름으로 매칭
    - 서비스 이용 내역 업데이트
    - 패키지 구매 정보 업데이트
    """
    try:
        # 엑셀 파일 읽기
        contents = await file.read()

        # 파일 형식에 따라 시트 읽기
        if file.filename and ('서비스' in file.filename or '이용' in file.filename):
            # 서비스 이용 내역 파일
            df = pd.read_excel(io.BytesIO(contents))
            return await process_service_usage(df, db, update_mode)

        elif file.filename and ('결제' in file.filename or '패키지' in file.filename):
            # 패키지 구매 내역 파일
            df = pd.read_excel(io.BytesIO(contents))
            return await process_package_purchases(df, db, update_mode)

        else:
            # 일반 고객 관리 파일 (서비스 이력 포함)
            xl_file = pd.ExcelFile(io.BytesIO(contents))

            # 시트별 처리
            results = {
                "customers_updated": 0,
                "service_records_added": 0,
                "package_records_added": 0,
                "errors": []
            }

            for sheet_name in xl_file.sheet_names:
                if '서비스' in sheet_name or '이용' in sheet_name:
                    df = pd.read_excel(xl_file, sheet_name=sheet_name)
                    result = await process_service_usage(df, db, update_mode)
                    results["service_records_added"] += result.get("success_count", 0)
                    results["errors"].extend(result.get("errors", []))

            return results

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일 처리 중 오류: {str(e)}")


async def process_service_usage(df: pd.DataFrame, db: Session, update_mode: str):
    """서비스 이용 내역 처리"""
    success_count = 0
    error_count = 0
    errors = []

    # 컬럼 매핑
    column_mapping = {
        '고객번호': 'customer_id',
        '고객ID': 'customer_id',
        '성함': 'customer_name',
        '이름': 'customer_name',
        '서비스일자': 'service_date',
        '이용일자': 'service_date',
        '서비스종류': 'service_type',
        '서비스명': 'service_type',
        '브레인': 'brain_count',
        '펄스': 'pulse_count',
        '림프': 'lymph_count',
        '레드': 'red_count',
        '비고': 'notes',
        '메모': 'notes'
    }

    df = df.rename(columns=column_mapping)

    for index, row in df.iterrows():
        try:
            # 고객 찾기
            customer = None

            # 1. 고객번호로 찾기
            if pd.notna(row.get('customer_id')):
                customer_id = int(row['customer_id'])
                customer = db.query(CustomerModel).filter(
                    CustomerModel.customer_id == customer_id
                ).first()

            # 2. 이름으로 찾기
            if not customer and pd.notna(row.get('customer_name')):
                customer_name = str(row['customer_name']).strip()
                customers = db.query(CustomerModel).filter(
                    CustomerModel.name == customer_name
                ).all()

                if len(customers) == 1:
                    customer = customers[0]
                elif len(customers) > 1:
                    error_count += 1
                    errors.append(f"행 {index + 2}: '{customer_name}' 이름의 고객이 {len(customers)}명 있습니다. 고객번호를 명시해주세요.")
                    continue

            if not customer:
                error_count += 1
                errors.append(f"행 {index + 2}: 고객을 찾을 수 없습니다")
                continue

            # 서비스 타입 결정
            service_type_id = None
            if pd.notna(row.get('service_type')):
                service_type_map = {
                    '브레인': 1, '브레인피드백': 1,
                    '펄스': 2, '펄스전자파': 2,
                    '림프': 3, '림프순환': 3,
                    '레드': 4, '레드테라피': 4
                }
                service_type = str(row['service_type']).strip()
                service_type_id = service_type_map.get(service_type)

            # 또는 개별 카운트에서 추론
            elif any(pd.notna(row.get(col)) and row.get(col) > 0 for col in ['brain_count', 'pulse_count', 'lymph_count', 'red_count']):
                if pd.notna(row.get('brain_count')) and row['brain_count'] > 0:
                    service_type_id = 1
                elif pd.notna(row.get('pulse_count')) and row['pulse_count'] > 0:
                    service_type_id = 2
                elif pd.notna(row.get('lymph_count')) and row['lymph_count'] > 0:
                    service_type_id = 3
                elif pd.notna(row.get('red_count')) and row['red_count'] > 0:
                    service_type_id = 4

            if not service_type_id:
                error_count += 1
                errors.append(f"행 {index + 2}: 서비스 종류를 확인할 수 없습니다")
                continue

            # 서비스 이용 기록 생성
            service_date = pd.to_datetime(row.get('service_date')) if pd.notna(row.get('service_date')) else datetime.now()

            # 기존 기록 확인 (중복 방지)
            existing = db.query(ServiceUsageModel).filter(
                ServiceUsageModel.customer_id == customer.customer_id,
                ServiceUsageModel.service_date == service_date,
                ServiceUsageModel.service_type_id == service_type_id
            ).first()

            if existing and update_mode == "merge":
                # 병합 모드: 스킵
                continue
            elif existing and update_mode == "replace":
                # 교체 모드: 기존 기록 삭제
                db.delete(existing)

            # 새 기록 생성
            service_usage = ServiceUsageModel(
                customer_id=customer.customer_id,
                service_date=service_date,
                service_type_id=service_type_id,
                notes=ExcelHandler.clean_string(row.get('notes'))
            )

            db.add(service_usage)
            success_count += 1

        except Exception as e:
            error_count += 1
            errors.append(f"행 {index + 2}: {str(e)}")

    db.commit()

    return {
        "message": "서비스 이력 가져오기 완료",
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors[:10]
    }


async def process_package_purchases(df: pd.DataFrame, db: Session, update_mode: str):
    """패키지 구매 내역 처리"""
    success_count = 0
    error_count = 0
    errors = []

    # 컬럼 매핑
    column_mapping = {
        '고객번호': 'customer_id',
        '고객ID': 'customer_id',
        '성함': 'customer_name',
        '이름': 'customer_name',
        '구매일': 'purchase_date',
        '결제일': 'purchase_date',
        '패키지명': 'package_name',
        '상품명': 'package_name',
        '브레인': 'brain_sessions',
        '펄스': 'pulse_sessions',
        '림프': 'lymph_sessions',
        '레드': 'red_sessions',
        '총횟수': 'total_sessions',
        '금액': 'price',
        '결제금액': 'price'
    }

    df = df.rename(columns=column_mapping)

    for index, row in df.iterrows():
        try:
            # 고객 찾기 (위와 동일한 로직)
            customer = None

            if pd.notna(row.get('customer_id')):
                customer_id = int(row['customer_id'])
                customer = db.query(CustomerModel).filter(
                    CustomerModel.customer_id == customer_id
                ).first()

            if not customer and pd.notna(row.get('customer_name')):
                customer_name = str(row['customer_name']).strip()
                customers = db.query(CustomerModel).filter(
                    CustomerModel.name == customer_name
                ).all()

                if len(customers) == 1:
                    customer = customers[0]
                elif len(customers) > 1:
                    error_count += 1
                    errors.append(f"행 {index + 2}: '{customer_name}' 이름의 고객이 {len(customers)}명 있습니다.")
                    continue

            if not customer:
                error_count += 1
                errors.append(f"행 {index + 2}: 고객을 찾을 수 없습니다")
                continue

            # 패키지 정보 추출
            package_data = {
                'customer_id': customer.customer_id,
                'purchase_date': pd.to_datetime(row.get('purchase_date')) if pd.notna(row.get('purchase_date')) else datetime.now(),
                'package_name': ExcelHandler.clean_string(row.get('package_name')) or '종합 패키지',
                'total_sessions': 0,
                'remaining_sessions': 0,
                'price': ExcelHandler.clean_number(row.get('price')) or 0
            }

            # 서비스별 세션 수 계산
            service_allocations = {}
            total_sessions = 0

            for service, col in [('브레인', 'brain_sessions'), ('펄스', 'pulse_sessions'),
                               ('림프', 'lymph_sessions'), ('레드', 'red_sessions')]:
                if pd.notna(row.get(col)) and row[col] > 0:
                    service_allocations[service] = int(row[col])
                    total_sessions += int(row[col])

            package_data['total_sessions'] = total_sessions or int(row.get('total_sessions', 0))
            package_data['remaining_sessions'] = package_data['total_sessions']  # 초기값
            package_data['service_allocations'] = service_allocations

            # 패키지 구매 기록 생성
            package_purchase = PackagePurchaseModel(**package_data)
            db.add(package_purchase)
            success_count += 1

        except Exception as e:
            error_count += 1
            errors.append(f"행 {index + 2}: {str(e)}")

    db.commit()

    return {
        "message": "패키지 구매 내역 가져오기 완료",
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors[:10]
    }
