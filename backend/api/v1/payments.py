from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import pandas as pd
import io
from dateutil.relativedelta import relativedelta
import re

from core.database import get_db
from models.payment import Payment as PaymentModel
from models.customer import Customer as CustomerModel
from schemas.payment import Payment, PaymentCreate, PaymentInDB

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
def get_payments(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    customer_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    payment_status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """결제 내역 조회 - 수정된 버전"""
    # 디버깅: 받은 파라미터 확인
    print(f"🔍 Payment search params: date_from={date_from}, date_to={date_to}, search={search}")
    
    try:
        # 기본 쿼리 with LEFT JOIN
        query = select(
            PaymentModel.payment_id,
            PaymentModel.payment_number,
            PaymentModel.customer_id,
            PaymentModel.payment_date,
            PaymentModel.amount,
            PaymentModel.payment_method,
            PaymentModel.payment_type,
            PaymentModel.payment_status,
            PaymentModel.payment_staff,
            PaymentModel.transaction_id,
            PaymentModel.card_holder_name,
            PaymentModel.reference_type,
            PaymentModel.reference_id,
            PaymentModel.notes,
            PaymentModel.created_at,
            CustomerModel.name.label('customer_name'),
            CustomerModel.phone.label('customer_phone')
        ).select_from(
            PaymentModel
        ).outerjoin(
            CustomerModel,
            PaymentModel.customer_id == CustomerModel.customer_id
        )

        # 필터 적용
        filters = []

        if date_from:
            filters.append(PaymentModel.payment_date >= date_from)
        if date_to:
            filters.append(PaymentModel.payment_date <= date_to)
        if customer_id:
            filters.append(PaymentModel.customer_id == customer_id)
        if payment_method:
            filters.append(PaymentModel.payment_method == payment_method)

        if payment_status:
            filters.append(PaymentModel.payment_status == payment_status)

        # 검색 조건
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    CustomerModel.name.ilike(search_pattern),
                    CustomerModel.phone.ilike(search_pattern)
                )
            )

        if filters:
            query = query.where(and_(*filters))
            print(f"🔍 Applied {len(filters)} filters")
        else:
            print(f"🔍 No filters applied - returning all payments")

        # 정렬 및 페이징
        query = query.order_by(PaymentModel.payment_date.desc(), PaymentModel.payment_id.desc())
        query = query.offset(skip).limit(limit)

        # 실행
        result = db.execute(query)
        payments = []

        for row in result:
            payment_dict = {
                "payment_id": row.payment_id,
                "payment_number": row.payment_number or "",
                "customer_id": row.customer_id,
                "customer_name": row.customer_name or "",
                "customer_phone": row.customer_phone or "",
                "payment_date": row.payment_date.isoformat() if row.payment_date else None,
                "amount": float(row.amount) if row.amount else 0.0,
                "payment_method": row.payment_method or "",
                "payment_type": row.payment_type or "single",
                "payment_status": row.payment_status or "completed",
                "payment_staff": row.payment_staff or "",
                "approval_number": row.transaction_id or "",
                "card_holder_name": row.card_holder_name or "",
                "purchase_type": row.reference_type or "",
                "purchase_order": row.reference_id,
                "notes": row.notes or "",
                "created_at": row.created_at.isoformat() if row.created_at else None
            }
            payments.append(payment_dict)

        print(f"🔍 Returning {len(payments)} payments")
        return payments

    except Exception as e:
        print(f"❌ 결제 조회 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_payment_stats(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """결제 통계 - 전월 매출 포함"""
    try:
        # 현재 날짜 기준
        today = datetime.now().date()

        # 전월 첫날과 마지막날 계산
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        # 기본 통계 쿼리 (필터 기간)
        query = select(
            func.count(func.distinct(PaymentModel.payment_id)).label('total_count'),
            func.sum(PaymentModel.amount).label('total_revenue'),
            func.count(func.distinct(PaymentModel.customer_id)).label('customer_count')
        )

        # 날짜 필터
        if date_from:
            query = query.where(PaymentModel.payment_date >= date_from)
        if date_to:
            query = query.where(PaymentModel.payment_date <= date_to)

        # 쿼리 로깅
        print(f"🔍 결제 통계 쿼리: {query}")

        result = db.execute(query).one()

        # 전월 매출 별도 쿼리
        last_month_query = select(
            func.sum(PaymentModel.amount).label('last_month_revenue')
        ).where(
            and_(
                PaymentModel.payment_date >= first_day_of_previous_month,
                PaymentModel.payment_date <= last_day_of_previous_month
            )
        )

        last_month_result = db.execute(last_month_query).one()
        last_month_revenue = float(last_month_result.last_month_revenue or 0)
        
        # 이번달 매출 쿼리
        current_month_query = select(
            func.sum(PaymentModel.amount).label('current_month_revenue')
        ).where(
            PaymentModel.payment_date >= first_day_of_current_month
        )
        
        current_month_result = db.execute(current_month_query).one()
        current_month_revenue = float(current_month_result.current_month_revenue or 0)

        # 최근 3개월 평균 결제액 계산
        three_months_ago = today - timedelta(days=90)
        avg_query = select(
            func.count(func.distinct(PaymentModel.payment_id)).label('count'),
            func.sum(PaymentModel.amount).label('total')
        ).where(
            PaymentModel.payment_date >= three_months_ago
        )

        avg_result = db.execute(avg_query).one()
        avg_amount = float(avg_result.total / avg_result.count) if avg_result.count > 0 else 0

        return {
            "total_count": result.total_count or 0,
            "total_revenue": last_month_revenue,  # 전월 매출
            "current_month_revenue": current_month_revenue,  # 이번달 매출
            "customer_count": result.customer_count or 0,
            "average_amount": avg_amount,  # 최근 3개월 기준
            "previous_month": f"{first_day_of_previous_month.year}년 {first_day_of_previous_month.month}월",
            "current_month": f"{first_day_of_current_month.year}년 {first_day_of_current_month.month}월"
        }

    except Exception as e:
        print(f"❌ 통계 조회 에러: {str(e)}")
        return {
            "total_count": 0,
            "total_revenue": 0,
            "customer_count": 0,
            "average_amount": 0
        }

@router.get("/stats/summary")
def get_payment_summary(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """결제 통계 요약 (프론트엔드 호환)"""
    # /stats 엔드포인트와 동일한 기능
    return get_payment_stats(date_from, date_to, db)

@router.post("/", response_model=Payment)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    """결제 등록"""
    # 고객 확인
    customer = db.query(CustomerModel).filter(
        CustomerModel.customer_id == payment.customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="고객을 찾을 수 없습니다.")

    # 결제 생성
    db_payment = PaymentModel(**payment.model_dump())

    # payment_number 자동 생성
    year = payment.payment_date.year
    # 해당 연도의 마지막 번호 찾기
    last_payment = db.query(PaymentModel).filter(
        PaymentModel.payment_number.like(f"PAY-{year}-%")
    ).order_by(PaymentModel.payment_number.desc()).first()

    if last_payment and last_payment.payment_number:
        # 마지막 번호에서 순번 추출
        last_num = int(last_payment.payment_number.split('-')[-1])
        new_num = last_num + 1
    else:
        # 해당 연도의 첫 번째 결제
        new_num = 1

    db_payment.payment_number = f"PAY-{year}-{new_num:06d}"

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment

@router.get("/{payment_id}", response_model=Payment)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """특정 결제 조회"""
    payment = db.query(PaymentModel).filter(
        PaymentModel.payment_id == payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="결제를 찾을 수 없습니다.")

    return payment

@router.put("/{payment_id}", response_model=Payment)
@router.put("/{payment_id}/", response_model=Payment, include_in_schema=False)
def update_payment(
    payment_id: int,
    payment_update: PaymentCreate,
    db: Session = Depends(get_db)
):
    """결제 수정"""
    payment = db.query(PaymentModel).filter(
        PaymentModel.payment_id == payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="결제를 찾을 수 없습니다.")

    for key, value in payment_update.model_dump().items():
        setattr(payment, key, value)

    db.commit()
    db.refresh(payment)

    return payment

@router.delete("/{payment_id}")
@router.delete("/{payment_id}/", include_in_schema=False)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    """결제 삭제"""
    payment = db.query(PaymentModel).filter(
        PaymentModel.payment_id == payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="결제를 찾을 수 없습니다.")

    db.delete(payment)
    db.commit()

    return {"message": "결제가 삭제되었습니다."}

@router.get("/export/excel", include_in_schema=False)
@router.get("/export/excel/")
def export_payments_to_excel(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    customer_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """결제 데이터를 엑셀 파일로 내보내기"""
    try:
        # 결제 데이터 조회 (동일한 로직)
        query = select(
            PaymentModel.payment_id,
            PaymentModel.payment_number,
            PaymentModel.customer_id,
            PaymentModel.payment_date,
            PaymentModel.amount,
            PaymentModel.payment_method,
            PaymentModel.payment_type,
            PaymentModel.payment_status,
            PaymentModel.payment_staff,
            PaymentModel.transaction_id,
            PaymentModel.card_holder_name,
            PaymentModel.reference_type,
            PaymentModel.reference_id,
            PaymentModel.notes,
            PaymentModel.created_at,
            CustomerModel.name.label('customer_name'),
            CustomerModel.phone.label('customer_phone')
        ).select_from(
            PaymentModel
        ).outerjoin(
            CustomerModel,
            PaymentModel.customer_id == CustomerModel.customer_id
        )

        # 필터 적용
        filters = []
        if date_from:
            filters.append(PaymentModel.payment_date >= date_from)
        if date_to:
            filters.append(PaymentModel.payment_date <= date_to)
        if customer_id:
            filters.append(PaymentModel.customer_id == customer_id)
        if payment_method:
            filters.append(PaymentModel.payment_method == payment_method)

        # 검색 조건
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    CustomerModel.name.ilike(search_pattern),
                    CustomerModel.phone.ilike(search_pattern),
                    PaymentModel.transaction_id.ilike(search_pattern)
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # 정렬
        query = query.order_by(PaymentModel.payment_date.desc(), PaymentModel.payment_id.desc())

        # 실행
        result = db.execute(query)

        # 데이터 준비
        data = []
        for row in result:
            data.append({
                "결제번호": row.payment_number or "",
                "결제ID": row.payment_id,
                "결제일": row.payment_date.strftime('%Y-%m-%d') if row.payment_date else "",
                "고객명": row.customer_name or "",
                "고객전화번호": row.customer_phone or "",
                "결제금액": float(row.amount) if row.amount else 0.0,
                "결제방법": row.payment_method or "",
                "결제유형": row.payment_type or "",
                "결제상태": row.payment_status or "",
                "담당직원": row.payment_staff or "",
                "승인번호": row.transaction_id or "",
                "카드명의자": row.card_holder_name or "",
                "구매항목": row.reference_type or "",
                "구매차수": row.reference_id or "",
                "메모": row.notes or "",
                "생성일시": row.created_at.strftime('%Y-%m-%d %H:%M:%S') if row.created_at else ""
            })

        # DataFrame 생성
        df = pd.DataFrame(data)

        if df.empty:
            df = pd.DataFrame(columns=[
                "결제번호", "결제ID", "결제일", "고객명", "고객전화번호", "결제금액",
                "결제방법", "결제유형", "결제상태", "담당직원", "승인번호",
                "카드명의자", "구매항목", "구매차수", "메모", "생성일시"
            ])

        # 엑셀 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='결제내역')

            # 워크시트 가져오기 및 스타일 적용
            worksheet = writer.sheets['결제내역']

            # 컬럼 너비 자동 조정
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)

        # 응답 생성
        headers = {
            'Content-Disposition': f'attachment; filename=payments_{date.today().strftime("%Y%m%d")}.xlsx'
        }

        return Response(
            content=output.getvalue(),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers=headers
        )

    except Exception as e:
        print(f"❌ 엑셀 내보내기 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"엑셀 내보내기 중 오류가 발생했습니다: {str(e)}")
