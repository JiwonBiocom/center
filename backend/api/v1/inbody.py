from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from core.database import get_db
from core.auth import get_current_user
from models.inbody import InBodyRecord
from models.customer import Customer
from schemas.inbody import InBodyRecord as InBodyRecordSchema, InBodyRecordCreate, InBodyRecordUpdate, InBodyRecordSummary
from utils.response_formatter import ResponseFormatter

class ManualInBodyCreate(BaseModel):
    customer_id: int
    weight: float
    body_fat_percentage: Optional[float] = None
    skeletal_muscle_mass: Optional[float] = None
    extracellular_water_ratio: Optional[float] = None
    phase_angle: Optional[float] = None
    visceral_fat_level: Optional[int] = None
    notes: Optional[str] = None

router = APIRouter(prefix="/inbody", tags=["inbody"])

@router.post("/", response_model=dict)
@router.post("/records", response_model=dict)
async def create_inbody_record(
    record_data: InBodyRecordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """인바디 기록 생성"""
    try:
        # 고객 존재 확인
        customer = db.query(Customer).filter(Customer.customer_id == record_data.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="고객을 찾을 수 없습니다."
            )

        # 인바디 기록 생성
        db_record = InBodyRecord(**record_data.model_dump())
        if not db_record.measured_by:
            db_record.measured_by = current_user.email

        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        response = ResponseFormatter.created(
            data=InBodyRecordSchema.from_orm(db_record),
            message="인바디 기록이 성공적으로 추가되었습니다."
        )
        return response.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인바디 기록 생성 실패: {str(e)}"
        )

@router.post("/manual", response_model=dict)
async def create_manual_inbody_record(
    record_data: ManualInBodyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """수동 인바디 기록 생성 (태블릿 문진용)"""
    try:
        # 고객 존재 확인
        customer = db.query(Customer).filter(Customer.customer_id == record_data.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="고객을 찾을 수 없습니다."
            )

        # 인바디 기록 생성
        db_record = InBodyRecord(
            customer_id=record_data.customer_id,
            weight=record_data.weight,
            body_fat_percentage=record_data.body_fat_percentage,
            skeletal_muscle_mass=record_data.skeletal_muscle_mass,
            extracellular_water_ratio=record_data.extracellular_water_ratio,
            phase_angle=record_data.phase_angle,
            visceral_fat_level=record_data.visceral_fat_level,
            notes=record_data.notes or "수동 입력",
            measured_by=current_user.name if hasattr(current_user, 'name') else current_user.email
        )

        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        response = ResponseFormatter.created(
            data=InBodyRecordSchema.from_orm(db_record),
            message="인바디 기록이 성공적으로 추가되었습니다."
        )
        return response.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인바디 기록 생성 실패: {str(e)}"
        )

@router.get("/customer/{customer_id}", response_model=dict)
async def get_customer_inbody_records(
    customer_id: int,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """특정 고객의 인바디 기록 조회"""
    try:
        # 고객 존재 확인
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="고객을 찾을 수 없습니다."
            )

        # 인바디 기록 조회 (최신순)
        records = db.query(InBodyRecord)\
            .filter(InBodyRecord.customer_id == customer_id)\
            .order_by(InBodyRecord.measurement_date.desc())\
            .limit(limit)\
            .all()

        # 요약 정보 계산
        total_records = db.query(InBodyRecord)\
            .filter(InBodyRecord.customer_id == customer_id)\
            .count()

        latest_record = records[0] if records else None

        # 트렌드 계산 (최근 2개 기록 비교)
        weight_trend = None
        body_fat_trend = None

        if len(records) >= 2:
            latest = records[0]
            previous = records[1]

            if latest.weight and previous.weight:
                if latest.weight > previous.weight:
                    weight_trend = "increasing"
                elif latest.weight < previous.weight:
                    weight_trend = "decreasing"
                else:
                    weight_trend = "stable"

            if latest.body_fat_percentage and previous.body_fat_percentage:
                if latest.body_fat_percentage > previous.body_fat_percentage:
                    body_fat_trend = "increasing"
                elif latest.body_fat_percentage < previous.body_fat_percentage:
                    body_fat_trend = "decreasing"
                else:
                    body_fat_trend = "stable"

        summary = InBodyRecordSummary(
            total_records=total_records,
            latest_record=InBodyRecordSchema.from_orm(latest_record) if latest_record else None,
            weight_trend=weight_trend,
            body_fat_trend=body_fat_trend
        )

        response = ResponseFormatter.success(
            data={
                "records": [InBodyRecordSchema.from_orm(record) for record in records],
                "summary": summary
            }
        )
        return response.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인바디 기록 조회 실패: {str(e)}"
        )

@router.get("/{record_id}", response_model=dict)
async def get_inbody_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """특정 인바디 기록 조회"""
    try:
        record = db.query(InBodyRecord).filter(InBodyRecord.record_id == record_id).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="인바디 기록을 찾을 수 없습니다."
            )

        response = ResponseFormatter.success(data=InBodyRecordSchema.from_orm(record))
        return response.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인바디 기록 조회 실패: {str(e)}"
        )

@router.put("/{record_id}", response_model=dict)
async def update_inbody_record(
    record_id: int,
    record_data: InBodyRecordUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """인바디 기록 수정"""
    try:
        record = db.query(InBodyRecord).filter(InBodyRecord.record_id == record_id).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="인바디 기록을 찾을 수 없습니다."
            )

        # 수정할 필드만 업데이트
        update_data = record_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

        record.updated_at = datetime.now()
        db.commit()
        db.refresh(record)

        response = ResponseFormatter.updated(
            data=InBodyRecordSchema.from_orm(record),
            message="인바디 기록이 성공적으로 수정되었습니다."
        )
        return response.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인바디 기록 수정 실패: {str(e)}"
        )

@router.delete("/{record_id}", response_model=dict)
async def delete_inbody_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """인바디 기록 삭제"""
    try:
        record = db.query(InBodyRecord).filter(InBodyRecord.record_id == record_id).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="인바디 기록을 찾을 수 없습니다."
            )

        db.delete(record)
        db.commit()

        response = ResponseFormatter.deleted(message="인바디 기록이 성공적으로 삭제되었습니다.")
        return response.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인바디 기록 삭제 실패: {str(e)}"
        )

@router.get("/customer/{customer_id}/chart-data", response_model=dict)
async def get_inbody_chart_data(
    customer_id: int,
    months: Optional[int] = 6,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """인바디 차트 데이터 조회"""
    try:
        # 고객 존재 확인
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="고객을 찾을 수 없습니다."
            )

        # 지정된 개월 수만큼의 데이터 조회
        start_date = datetime.now() - timedelta(days=months * 30)

        records = db.query(InBodyRecord)\
            .filter(
                InBodyRecord.customer_id == customer_id,
                InBodyRecord.measurement_date >= start_date
            )\
            .order_by(InBodyRecord.measurement_date.asc())\
            .all()

        # 차트 데이터 준비
        chart_data = {
            "dates": [],
            "weight": [],
            "body_fat_percentage": [],
            "skeletal_muscle_mass": [],
            "visceral_fat_level": []
        }

        for record in records:
            chart_data["dates"].append(record.measurement_date.strftime("%Y-%m-%d"))
            chart_data["weight"].append(record.weight)
            chart_data["body_fat_percentage"].append(record.body_fat_percentage)
            chart_data["skeletal_muscle_mass"].append(record.skeletal_muscle_mass)
            chart_data["visceral_fat_level"].append(record.visceral_fat_level)

        response = ResponseFormatter.success(data=chart_data)
        return response.model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"차트 데이터 조회 실패: {str(e)}"
        )
