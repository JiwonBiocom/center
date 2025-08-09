from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime
import pandas as pd
from io import BytesIO
import re

from core.database import get_db
from core.auth import get_current_user
from models.kit import KitManagement, KitType
from models.user import User
from models.customer import Customer
from schemas.kit import (
    KitType as KitTypeSchema,
    KitTypeCreate,
    KitTypeUpdate,
    KitTypeListResponse,
    KitManagement as KitManagementSchema,
    KitManagementCreate,
    KitManagementUpdate,
    KitManagementListResponse,
    KitManagementWithRelations
)

router = APIRouter()

# Kit Type Endpoints
@router.get("/kit-types", response_model=KitTypeListResponse)
async def list_kit_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """모든 검사키트 종류 조회"""
    query = db.query(KitType)

    if is_active is not None:
        query = query.filter(KitType.is_active == is_active)

    total = query.count()
    kit_types = query.offset(skip).limit(limit).all()

    return {
        "kit_types": kit_types,
        "total": total
    }

@router.get("/kit-types/{kit_type_id}", response_model=KitTypeSchema)
async def get_kit_type(
    kit_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 검사키트 종류 조회"""
    kit_type = db.query(KitType).filter(KitType.kit_type_id == kit_type_id).first()
    if not kit_type:
        raise HTTPException(status_code=404, detail="Kit type not found")
    return kit_type

@router.post("/kit-types", response_model=KitTypeSchema)
async def create_kit_type(
    kit_type: KitTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새로운 검사키트 종류 생성"""
    # 중복 코드 확인
    existing = db.query(KitType).filter(KitType.code == kit_type.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kit type with this code already exists")

    db_kit_type = KitType(**kit_type.model_dump())
    db.add(db_kit_type)
    db.commit()
    db.refresh(db_kit_type)
    return db_kit_type

@router.patch("/kit-types/{kit_type_id}", response_model=KitTypeSchema)
async def update_kit_type(
    kit_type_id: int,
    kit_type: KitTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """검사키트 종류 수정"""
    db_kit_type = db.query(KitType).filter(KitType.kit_type_id == kit_type_id).first()
    if not db_kit_type:
        raise HTTPException(status_code=404, detail="Kit type not found")

    update_data = kit_type.model_dump(exclude_unset=True)

    # 코드 중복 확인
    if "code" in update_data:
        existing = db.query(KitType).filter(
            KitType.code == update_data["code"],
            KitType.kit_type_id != kit_type_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Kit type with this code already exists")

    for key, value in update_data.items():
        setattr(db_kit_type, key, value)

    db.commit()
    db.refresh(db_kit_type)
    return db_kit_type

# 통계 및 대시보드 엔드포인트 (더 구체적인 경로를 먼저 정의)
@router.get("/stats/summary")
async def get_kit_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """검사키트 통계 조회"""
    query = db.query(KitManagement)

    if start_date:
        query = query.filter(KitManagement.created_at >= start_date)
    if end_date:
        query = query.filter(KitManagement.created_at <= end_date)

    total_kits = query.count()
    pending_kits = query.filter(KitManagement.received_date.is_(None)).count()
    in_progress_kits = query.filter(
        KitManagement.received_date.isnot(None),
        KitManagement.result_delivered_date.is_(None)
    ).count()
    completed_kits = query.filter(KitManagement.result_delivered_date.isnot(None)).count()

    # 키트 타입별 통계
    kit_type_stats = db.query(
        KitType.name,
        func.count(KitManagement.kit_id).label('count')
    ).join(
        KitManagement, KitManagement.kit_type_id == KitType.kit_type_id
    ).group_by(KitType.name).all()

    return {
        "total_kits": total_kits,
        "pending_kits": pending_kits,
        "in_progress_kits": in_progress_kits,
        "completed_kits": completed_kits,
        "completion_rate": round(completed_kits / total_kits * 100, 1) if total_kits > 0 else 0,
        "kit_type_stats": [
            {"name": stat[0], "count": stat[1]} for stat in kit_type_stats
        ]
    }

# Kit Management Endpoints
@router.get("/")
async def list_kits(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    customer_id: Optional[int] = None,
    kit_type_id: Optional[int] = None,
    status: Optional[str] = None,  # pending, in_progress, completed
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """검사키트 목록 조회"""
    query = db.query(KitManagement).options(
        joinedload(KitManagement.customer),
        joinedload(KitManagement.kit_type_ref)
    )

    if customer_id:
        query = query.filter(KitManagement.customer_id == customer_id)

    if kit_type_id:
        query = query.filter(KitManagement.kit_type_id == kit_type_id)

    # 상태 필터링
    if status == "pending":
        query = query.filter(KitManagement.received_date.is_(None))
    elif status == "in_progress":
        query = query.filter(
            KitManagement.received_date.isnot(None),
            KitManagement.result_delivered_date.is_(None)
        )
    elif status == "completed":
        query = query.filter(KitManagement.result_delivered_date.isnot(None))

    total = query.count()
    kits = query.order_by(KitManagement.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "kits": kits,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }

@router.get("/{kit_id}", response_model=KitManagementWithRelations)
async def get_kit(
    kit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """특정 검사키트 조회"""
    kit = db.query(KitManagement).options(
        joinedload(KitManagement.customer),
        joinedload(KitManagement.kit_type_ref)
    ).filter(KitManagement.kit_id == kit_id).first()

    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    return kit

@router.post("/", response_model=KitManagementSchema)
async def create_kit(
    kit: KitManagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """새로운 검사키트 생성"""
    # 고객 확인
    customer = db.query(Customer).filter(Customer.customer_id == kit.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # 키트 타입 확인
    kit_type = db.query(KitType).filter(KitType.kit_type_id == kit.kit_type_id).first()
    if not kit_type:
        raise HTTPException(status_code=404, detail="Kit type not found")

    # 시리얼 번호 중복 확인
    if kit.serial_number:
        existing = db.query(KitManagement).filter(
            KitManagement.serial_number == kit.serial_number
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Serial number already exists")

    db_kit = KitManagement(
        **kit.model_dump(),
        kit_type=kit_type.name  # kit_type 필드에 이름 저장
    )
    db.add(db_kit)
    db.commit()
    db.refresh(db_kit)
    return db_kit

@router.patch("/{kit_id}")
async def update_kit(
    kit_id: int,
    kit: KitManagementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """검사키트 정보 수정"""
    try:
        print(f"Updating kit {kit_id} with data: {kit.model_dump()}")

        db_kit = db.query(KitManagement).filter(KitManagement.kit_id == kit_id).first()
        if not db_kit:
            raise HTTPException(status_code=404, detail="Kit not found")

        update_data = kit.model_dump(exclude_unset=True)
        print(f"Update data: {update_data}")

        # 고객 변경 시 확인
        if "customer_id" in update_data:
            customer = db.query(Customer).filter(Customer.customer_id == update_data["customer_id"]).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")

        # 키트 타입 변경 시 확인
        if "kit_type_id" in update_data:
            kit_type = db.query(KitType).filter(KitType.kit_type_id == update_data["kit_type_id"]).first()
            if not kit_type:
                raise HTTPException(status_code=404, detail="Kit type not found")
            # kit_type 문자열 필드도 업데이트
            db_kit.kit_type = kit_type.name

        # 시리얼 번호 중복 확인
        if "serial_number" in update_data and update_data["serial_number"]:
            existing = db.query(KitManagement).filter(
                KitManagement.serial_number == update_data["serial_number"],
                KitManagement.kit_id != kit_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Serial number already exists")

        for key, value in update_data.items():
            print(f"Setting {key} = {value}")
            setattr(db_kit, key, value)

        db.commit()
        db.refresh(db_kit)

        # 관계 데이터를 다시 로드하여 응답
        updated_kit = db.query(KitManagement).options(
            joinedload(KitManagement.customer),
            joinedload(KitManagement.kit_type_ref)
        ).filter(KitManagement.kit_id == kit_id).first()

        # SQLAlchemy 객체를 수동으로 딕셔너리로 변환하여 Pydantic 시리얼화 에러 방지
        result = {
            "kit_id": updated_kit.kit_id,
            "customer_id": updated_kit.customer_id,
            "kit_type": updated_kit.kit_type,
            "kit_type_id": updated_kit.kit_type_id,
            "serial_number": updated_kit.serial_number,
            "received_date": updated_kit.received_date.isoformat() if updated_kit.received_date else None,
            "result_received_date": updated_kit.result_received_date.isoformat() if updated_kit.result_received_date else None,
            "result_delivered_date": updated_kit.result_delivered_date.isoformat() if updated_kit.result_delivered_date else None,
            "created_at": updated_kit.created_at.isoformat() if updated_kit.created_at else None,
            "customer": {
                "customer_id": updated_kit.customer.customer_id,
                "name": updated_kit.customer.name,
                "phone": updated_kit.customer.phone
            } if updated_kit.customer else None,
            "kit_type_ref": {
                "kit_type_id": updated_kit.kit_type_ref.kit_type_id,
                "name": updated_kit.kit_type_ref.name,
                "code": updated_kit.kit_type_ref.code,
                "description": updated_kit.kit_type_ref.description,
                "price": updated_kit.kit_type_ref.price,
                "is_active": updated_kit.kit_type_ref.is_active
            } if updated_kit.kit_type_ref else None
        }

        print(f"Kit updated successfully: {result['kit_id']}")
        return result

    except Exception as e:
        print(f"Error updating kit {kit_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.delete("/{kit_id}")
async def delete_kit(
    kit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """검사키트 삭제"""
    db_kit = db.query(KitManagement).filter(KitManagement.kit_id == kit_id).first()
    if not db_kit:
        raise HTTPException(status_code=404, detail="Kit not found")

    db.delete(db_kit)
    db.commit()
    return {"detail": "Kit deleted successfully"}

# Excel Export/Import Endpoints
@router.get("/export/excel")
async def export_kits_to_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """검사키트 데이터를 엑셀로 다운로드"""
    try:
        # 데이터 조회
        kits = db.query(KitManagement).options(
            joinedload(KitManagement.customer),
            joinedload(KitManagement.kit_type_ref)
        ).order_by(KitManagement.created_at.desc()).all()

        # 데이터프레임 생성
        data = []
        for kit in kits:
            data.append({
                "키트ID": kit.kit_id,
                "고객명": kit.customer.name if kit.customer else "",
                "고객전화번호": kit.customer.phone if kit.customer else "",
                "키트종류": kit.kit_type,
                "시리얼번호": kit.serial_number or "",
                "키트수령일": kit.received_date.strftime("%Y-%m-%d") if kit.received_date else "",
                "결과수령일": kit.result_received_date.strftime("%Y-%m-%d") if kit.result_received_date else "",
                "결과전달일": kit.result_delivered_date.strftime("%Y-%m-%d") if kit.result_delivered_date else "",
                "상태": get_kit_status(kit),
                "등록일": kit.created_at.strftime("%Y-%m-%d %H:%M:%S") if kit.created_at else ""
            })

        df = pd.DataFrame(data)

        # Excel 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='검사키트목록', index=False)

            # 컬럼 너비 자동 조정
            worksheet = writer.sheets['검사키트목록']
            for column in df:
                column_width = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                worksheet.column_dimensions[chr(65 + col_idx)].width = min(column_width + 2, 50)

        output.seek(0)

        # 파일명 생성 (한글 제거)
        filename = f"kits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return StreamingResponse(
            BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        print(f"Excel export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Excel export failed: {str(e)}")

@router.post("/import/excel")
async def import_kits_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """엑셀 파일에서 검사키트 데이터 업로드"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.")

    try:
        # 파일 읽기
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        # 필수 컬럼 확인
        required_columns = ["고객명", "키트종류"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"필수 컬럼이 없습니다: {', '.join(missing_columns)}"
            )

        # 데이터 처리
        success_count = 0
        error_count = 0
        errors = []

        # 키트 타입 맵핑
        kit_types = db.query(KitType).all()
        kit_type_map = {kt.name: kt.kit_type_id for kt in kit_types}

        for idx, row in df.iterrows():
            try:
                # 고객명으로 고객 찾기
                customer_name = str(row.get('고객명', '')).strip()
                if not customer_name:
                    raise ValueError("고객명이 없습니다")

                # 전화번호 정리
                phone = clean_phone_number(row.get('고객전화번호', ''))

                # 고객 찾기 또는 생성
                customer = db.query(Customer).filter(Customer.name == customer_name).first()
                if not customer and phone:
                    customer = db.query(Customer).filter(Customer.phone == phone).first()

                if not customer:
                    # 새 고객 생성
                    customer = Customer(name=customer_name, phone=phone)
                    db.add(customer)
                    db.flush()

                # 키트 타입 확인
                kit_type_name = str(row.get('키트종류', '')).strip()
                kit_type_id = kit_type_map.get(kit_type_name)

                # 시리얼 번호 중복 확인
                serial_number = row.get('시리얼번호')
                if serial_number:
                    serial_number = str(serial_number).strip()
                    existing = db.query(KitManagement).filter(
                        KitManagement.serial_number == serial_number
                    ).first()
                    if existing:
                        # 기존 레코드 업데이트
                        update_kit_from_row(existing, row, customer.customer_id, kit_type_id)
                    else:
                        # 새 레코드 생성
                        new_kit = create_kit_from_row(row, customer.customer_id, kit_type_id, kit_type_name)
                        db.add(new_kit)
                else:
                    # 시리얼 번호가 없으면 새 레코드 생성
                    new_kit = create_kit_from_row(row, customer.customer_id, kit_type_id, kit_type_name)
                    db.add(new_kit)

                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"행 {idx + 2}: {str(e)}")
                db.rollback()
                continue

        # 커밋
        db.commit()

        return {
            "success": True,
            "message": f"업로드 완료: 성공 {success_count}건, 실패 {error_count}건",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]  # 최대 10개 에러만 반환
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일 처리 중 오류 발생: {str(e)}")

def get_kit_status(kit: KitManagement) -> str:
    """키트 상태 확인"""
    if not kit.received_date:
        return "대기"
    elif not kit.result_delivered_date:
        return "진행중"
    else:
        return "완료"

def clean_phone_number(phone):
    """전화번호 정리"""
    if pd.isna(phone) or not phone:
        return None

    phone = str(phone).strip()
    phone = re.sub(r'[^\d]', '', phone)

    if len(phone) in [10, 11]:
        if len(phone) == 10:
            return f"010-{phone[3:7]}-{phone[7:]}"
        else:
            return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"

    return None

def parse_date(date_value):
    """날짜 파싱"""
    if pd.isna(date_value) or not date_value:
        return None

    if isinstance(date_value, pd.Timestamp):
        return date_value.date()

    if isinstance(date_value, str):
        try:
            return pd.to_datetime(date_value).date()
        except:
            return None

    return None

def create_kit_from_row(row, customer_id: int, kit_type_id: Optional[int], kit_type_name: str) -> KitManagement:
    """엑셀 행에서 KitManagement 객체 생성"""
    return KitManagement(
        customer_id=customer_id,
        kit_type=kit_type_name,
        kit_type_id=kit_type_id,
        serial_number=row.get('시리얼번호'),
        received_date=parse_date(row.get('키트수령일')),
        result_received_date=parse_date(row.get('결과수령일')),
        result_delivered_date=parse_date(row.get('결과전달일'))
    )

def update_kit_from_row(kit: KitManagement, row, customer_id: int, kit_type_id: Optional[int]):
    """엑셀 행 데이터로 기존 키트 업데이트"""
    kit.customer_id = customer_id
    if kit_type_id:
        kit.kit_type_id = kit_type_id

    # 날짜 필드 업데이트
    received_date = parse_date(row.get('키트수령일'))
    if received_date:
        kit.received_date = received_date

    result_received_date = parse_date(row.get('결과수령일'))
    if result_received_date:
        kit.result_received_date = result_received_date

    result_delivered_date = parse_date(row.get('결과전달일'))
    if result_delivered_date:
        kit.result_delivered_date = result_delivered_date
