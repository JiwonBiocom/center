"""
유입고객 관리 API - 라우터 순서 수정 버전
"""
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
import pandas as pd
from io import BytesIO
import json
from pydantic import BaseModel

from core.database import get_db
from core.auth import get_current_user
from models.user import User
from models.customer_extended import MarketingLead
from models.lead_management import LeadConsultationHistory, ReregistrationCampaign, CampaignTarget
from models.customer import Customer
from schemas.lead import (
    MarketingLead as MarketingLeadSchema,
    MarketingLeadCreate,
    MarketingLeadUpdate,
    MarketingLeadFilter,
    ConsultationHistory,
    ConsultationHistoryCreate,
    Campaign,
    CampaignCreate,
    CampaignUpdate,
    CampaignTarget,
    CampaignTargetCreate
)
from utils.response_formatter import paginate_query

router = APIRouter(
    prefix="/api/v1/customer-leads",
    tags=["customer-leads"]
)

# ========== 정적 경로들을 먼저 정의 ==========

@router.get("/")
def get_customer_leads(
    # 필터 파라미터
    db_entry_date_from: Optional[date] = None,
    db_entry_date_to: Optional[date] = None,
    lead_date_from: Optional[date] = None,
    lead_date_to: Optional[date] = None,
    status: Optional[List[str]] = Query(None),
    lead_channel: Optional[List[str]] = Query(None),
    db_channel: Optional[List[str]] = Query(None),
    region: Optional[List[str]] = Query(None),
    assigned_staff_id: Optional[int] = None,
    is_reregistration_target: Optional[bool] = None,
    has_phone_consult: Optional[bool] = None,
    has_visit_consult: Optional[bool] = None,
    is_registered: Optional[bool] = None,
    age_from: Optional[int] = None,
    age_to: Optional[int] = None,
    search: Optional[str] = None,
    # 페이지네이션
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    # 인증
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객 목록 조회 (고급 필터링)"""
    try:
        query = db.query(MarketingLead).options(
            joinedload(MarketingLead.assigned_staff),
            joinedload(MarketingLead.converted_customer)
        )
        
        # 필터 적용
        if db_entry_date_from:
            query = query.filter(MarketingLead.db_entry_date >= db_entry_date_from)
        if db_entry_date_to:
            query = query.filter(MarketingLead.db_entry_date <= db_entry_date_to)
        if lead_date_from:
            query = query.filter(MarketingLead.lead_date >= lead_date_from)
        if lead_date_to:
            query = query.filter(MarketingLead.lead_date <= lead_date_to)
        
        if status:
            query = query.filter(MarketingLead.status.in_(status))
        if lead_channel:
            query = query.filter(MarketingLead.lead_channel.in_(lead_channel))
        if db_channel:
            query = query.filter(MarketingLead.db_channel.in_(db_channel))
        if region:
            query = query.filter(MarketingLead.region.in_(region))
        
        if assigned_staff_id:
            query = query.filter(MarketingLead.assigned_staff_id == assigned_staff_id)
        if is_reregistration_target is not None:
            query = query.filter(MarketingLead.is_reregistration_target == is_reregistration_target)
        
        if has_phone_consult is not None:
            if has_phone_consult:
                query = query.filter(MarketingLead.phone_consult_date.isnot(None))
            else:
                query = query.filter(MarketingLead.phone_consult_date.is_(None))
        
        if has_visit_consult is not None:
            if has_visit_consult:
                query = query.filter(MarketingLead.visit_consult_date.isnot(None))
            else:
                query = query.filter(MarketingLead.visit_consult_date.is_(None))
        
        if is_registered is not None:
            if is_registered:
                query = query.filter(MarketingLead.registration_date.isnot(None))
            else:
                query = query.filter(MarketingLead.registration_date.is_(None))
        
        if age_from:
            query = query.filter(MarketingLead.age >= age_from)
        if age_to:
            query = query.filter(MarketingLead.age <= age_to)
        
        # 검색
        if search:
            search_filter = or_(
                MarketingLead.name.ilike(f"%{search}%"),
                MarketingLead.phone.ilike(f"%{search}%"),
                MarketingLead.notes.ilike(f"%{search}%"),
                MarketingLead.carrot_id.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # 정렬
        try:
            if hasattr(MarketingLead, sort_by):
                if sort_order == "desc":
                    query = query.order_by(desc(getattr(MarketingLead, sort_by)))
                else:
                    query = query.order_by(asc(getattr(MarketingLead, sort_by)))
            else:
                # 기본 정렬
                query = query.order_by(desc(MarketingLead.created_at))
        except Exception as e:
            # 에러 시 기본 정렬
            query = query.order_by(desc(MarketingLead.created_at))
        
        # 페이지네이션
        result = paginate_query(query, page, page_size)
        
        # 관계 필드 추가
        for item in result["items"]:
            if hasattr(item, 'assigned_staff') and item.assigned_staff:
                item.assigned_staff_name = item.assigned_staff.name
            if hasattr(item, 'converted_customer') and item.converted_customer:
                item.converted_customer_name = item.converted_customer.name
        
        return result
    except Exception as e:
        import traceback
        print(f"Error in get_customer_leads: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_customer_lead_stats(
    db_entry_date_from: Optional[date] = None,
    db_entry_date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객 통계 조회"""
    base_query = db.query(MarketingLead)
    
    if db_entry_date_from:
        base_query = base_query.filter(MarketingLead.db_entry_date >= db_entry_date_from)
    if db_entry_date_to:
        base_query = base_query.filter(MarketingLead.db_entry_date <= db_entry_date_to)
    
    # 전체 통계
    total_count = base_query.count()
    converted_count = base_query.filter(MarketingLead.registration_date.isnot(None)).count()
    
    # 채널별 통계
    channel_stats = db.query(
        MarketingLead.lead_channel,
        func.count(MarketingLead.lead_id).label('count'),
        func.count(MarketingLead.registration_date).label('converted_count')
    ).filter(
        MarketingLead.lead_channel.isnot(None)
    ).group_by(MarketingLead.lead_channel).all()
    
    # 상태별 통계
    status_stats = db.query(
        MarketingLead.status,
        func.count(MarketingLead.lead_id).label('count')
    ).group_by(MarketingLead.status).all()
    
    # 월별 트렌드
    monthly_trend = db.query(
        func.date_trunc('month', MarketingLead.db_entry_date).label('month'),
        func.count(MarketingLead.lead_id).label('count'),
        func.count(MarketingLead.registration_date).label('converted_count')
    ).filter(
        MarketingLead.db_entry_date.isnot(None)
    ).group_by('month').order_by('month').all()
    
    return {
        "total_count": total_count,
        "converted_count": converted_count,
        "conversion_rate": round(converted_count / total_count * 100, 1) if total_count > 0 else 0,
        "channel_stats": [
            {
                "channel": stat.lead_channel,
                "count": stat.count,
                "converted_count": stat.converted_count,
                "conversion_rate": round(stat.converted_count / stat.count * 100, 1) if stat.count > 0 else 0
            }
            for stat in channel_stats
        ],
        "status_stats": [
            {"status": stat.status, "count": stat.count}
            for stat in status_stats
        ],
        "monthly_trend": [
            {
                "month": trend.month.strftime("%Y-%m"),
                "count": trend.count,
                "converted_count": trend.converted_count
            }
            for trend in monthly_trend
        ]
    }


@router.get("/reregistration-targets")
def get_reregistration_targets(
    last_service_date_before: Optional[date] = None,
    include_no_registration: bool = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """재등록 대상 조회"""
    query = db.query(MarketingLead).filter(
        MarketingLead.is_reregistration_target == True
    )
    
    if last_service_date_before:
        query = query.filter(
            or_(
                MarketingLead.last_service_date <= last_service_date_before,
                MarketingLead.last_service_date.is_(None)
            )
        )
    
    if not include_no_registration:
        query = query.filter(MarketingLead.registration_date.isnot(None))
    
    query = query.order_by(desc(MarketingLead.last_service_date))
    
    return paginate_query(query, page, page_size)


@router.get("/export")
def export_leads(
    format: str = Query("excel"),
    # 필터 파라미터 (위와 동일)
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객 데이터 내보내기"""
    # format 검증
    if format not in ["excel", "csv"]:
        format = "excel"
    
    # 필터 적용된 쿼리 생성
    query = db.query(MarketingLead)
    
    leads = query.all()
    
    # DataFrame 생성
    data = []
    for lead in leads:
        data.append({
            '이름': lead.name,
            '연락처': lead.phone,
            '나이': lead.age,
            '거주지역': lead.region,
            '유입경로': lead.lead_channel,
            'DB작성 채널': lead.db_channel,
            '당근아이디': lead.carrot_id,
            '시청 광고': lead.ad_watched,
            '가격안내': '예' if lead.price_informed else '아니오',
            'DB입력일': lead.db_entry_date,
            '전화상담일': lead.phone_consult_date,
            '방문상담일': lead.visit_consult_date,
            '등록일': lead.registration_date,
            '구매상품': lead.purchased_product,
            '미등록사유': lead.no_registration_reason,
            '비고': lead.notes,
            '매출': lead.revenue
        })
    
    df = pd.DataFrame(data)
    
    # 파일 생성
    output = BytesIO()
    if format == "excel":
        df.to_excel(output, index=False)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"유입고객_{date.today()}.xlsx"
    else:
        df.to_csv(output, index=False, encoding='utf-8-sig')
        media_type = "text/csv; charset=utf-8"
        filename = f"유입고객_{date.today()}.csv"
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.post("/")
def create_customer_lead(
    lead: MarketingLeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객 생성"""
    # 중복 체크 (전화번호 기준)
    if lead.phone:
        existing = db.query(MarketingLead).filter(
            MarketingLead.phone == lead.phone
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 전화번호입니다"
            )
    
    db_lead = MarketingLead(**lead.dict())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    return db_lead


class AssignStaffRequest(BaseModel):
    lead_ids: List[int]
    staff_id: int


@router.post("/assign-staff")
def assign_staff_bulk(
    request: AssignStaffRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """담당자 일괄 지정"""
    # 담당자 확인
    staff = db.query(User).filter(User.user_id == request.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="담당자를 찾을 수 없습니다")
    
    # 리드 업데이트
    updated_count = db.query(MarketingLead).filter(
        MarketingLead.lead_id.in_(request.lead_ids)
    ).update(
        {"assigned_staff_id": request.staff_id, "updated_at": datetime.now()},
        synchronize_session=False
    )
    
    db.commit()
    
    return {
        "message": f"{updated_count}명의 유입고객에게 담당자가 지정되었습니다",
        "updated_count": updated_count
    }


@router.post("/bulk-import")
async def bulk_import_leads(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """엑셀 파일로 유입고객 일괄 등록"""
    # 파일 읽기
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))
    
    # 컬럼 매핑
    column_mapping = {
        '이름': 'name',
        '연락처': 'phone',
        '나이': 'age',
        '거주지역': 'region',
        '유입경로': 'lead_channel',
        'DB작성 채널': 'db_channel',
        '당근아이디': 'carrot_id',
        '시청 광고': 'ad_watched',
        '가격안내': 'price_informed',
        'A/B 테스트': 'ab_test_group',
        'DB입력일': 'db_entry_date',
        '전화상담일': 'phone_consult_date',
        '방문상담일': 'visit_consult_date',
        '등록일': 'registration_date',
        '구매상품': 'purchased_product',
        '미등록사유': 'no_registration_reason',
        '비고': 'notes',
        '매출': 'revenue'
    }
    
    # 데이터 처리
    success_count = 0
    error_count = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            lead_data = {}
            for excel_col, db_col in column_mapping.items():
                if excel_col in row and pd.notna(row[excel_col]):
                    lead_data[db_col] = row[excel_col]
            
            # lead_date 설정
            if 'db_entry_date' in lead_data:
                lead_data['lead_date'] = lead_data['db_entry_date']
            else:
                lead_data['lead_date'] = date.today()
            
            # 중복 체크
            if 'phone' in lead_data:
                existing = db.query(MarketingLead).filter(
                    MarketingLead.phone == lead_data['phone']
                ).first()
                if existing:
                    error_count += 1
                    errors.append(f"행 {index + 2}: 중복된 전화번호")
                    continue
            
            # 리드 생성
            db_lead = MarketingLead(**lead_data)
            db.add(db_lead)
            success_count += 1
            
        except Exception as e:
            error_count += 1
            errors.append(f"행 {index + 2}: {str(e)}")
    
    db.commit()
    
    return {
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors[:10]  # 처음 10개 에러만 반환
    }


# ========== 파라미터가 있는 경로들 ==========

@router.get("/{lead_id}")
def get_customer_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객 상세 조회"""
    lead = db.query(MarketingLead).options(
        joinedload(MarketingLead.assigned_staff),
        joinedload(MarketingLead.converted_customer),
        joinedload(MarketingLead.consultation_history)
    ).filter(MarketingLead.lead_id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="유입고객을 찾을 수 없습니다")
    
    # 관계 필드 추가
    if lead.assigned_staff:
        lead.assigned_staff_name = lead.assigned_staff.name
    if lead.converted_customer:
        lead.converted_customer_name = lead.converted_customer.name
    
    return lead


@router.put("/{lead_id}")
def update_customer_lead(
    lead_id: int,
    lead_update: MarketingLeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객 수정"""
    db_lead = db.query(MarketingLead).filter(MarketingLead.lead_id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="유입고객을 찾을 수 없습니다")
    
    # 전화번호 중복 체크
    if lead_update.phone and lead_update.phone != db_lead.phone:
        existing = db.query(MarketingLead).filter(
            and_(
                MarketingLead.phone == lead_update.phone,
                MarketingLead.lead_id != lead_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 전화번호입니다"
            )
    
    # 업데이트
    update_data = lead_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lead, field, value)
    
    db_lead.updated_at = datetime.now()
    db.commit()
    db.refresh(db_lead)
    
    return db_lead


@router.delete("/{lead_id}")
def delete_customer_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객 삭제"""
    db_lead = db.query(MarketingLead).filter(MarketingLead.lead_id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="유입고객을 찾을 수 없습니다")
    
    db.delete(db_lead)
    db.commit()
    
    return {"message": "유입고객이 삭제되었습니다"}


# ========== 중첩된 경로들 ==========

@router.get("/{lead_id}/consultations")
def get_consultation_history(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """상담 이력 조회"""
    consultations = db.query(LeadConsultationHistory).options(
        joinedload(LeadConsultationHistory.created_by_user)
    ).filter(
        LeadConsultationHistory.lead_id == lead_id
    ).order_by(desc(LeadConsultationHistory.consultation_date)).all()
    
    # 생성자 이름 추가
    for consultation in consultations:
        if consultation.created_by_user:
            consultation.created_by_name = consultation.created_by_user.name
    
    return consultations


@router.post("/{lead_id}/consultations")
def add_consultation_history(
    lead_id: int,
    consultation: ConsultationHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """상담 이력 추가"""
    # 리드 확인
    lead = db.query(MarketingLead).filter(MarketingLead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="유입고객을 찾을 수 없습니다")
    
    # 상담 이력 생성
    db_consultation = LeadConsultationHistory(
        **consultation.dict(),
        created_by=current_user.user_id
    )
    db.add(db_consultation)
    
    # 리드 상태 업데이트
    if consultation.consultation_type == "phone":
        lead.phone_consult_date = consultation.consultation_date.date()
        lead.phone_consult_result = consultation.result
        if lead.status == "new":
            lead.status = "phone_consulted"
    elif consultation.consultation_type == "visit":
        lead.visit_consult_date = consultation.consultation_date.date()
        if lead.status in ["new", "phone_consulted"]:
            lead.status = "visit_consulted"
    
    db.commit()
    db.refresh(db_consultation)
    
    # 생성자 정보 추가
    db_consultation.created_by_name = current_user.name
    
    return db_consultation