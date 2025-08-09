"""
유입고객 관리 API - 라우터 순서 수정 버전
"""
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, Integer
import pandas as pd
from io import BytesIO
import json
from pydantic import BaseModel

from core.database import get_db
from core.auth import get_current_user
from models.user import User
from models.customer_extended import MarketingLead
from models.lead_management import LeadConsultationHistory, ReregistrationCampaign, CampaignTarget as CampaignTargetModel
from models.customer import Customer
from schemas.lead import (
    MarketingLead as MarketingLeadSchema,
    MarketingLeadCreate,
    MarketingLeadUpdate,
    MarketingLeadFilter,
    ConsultationHistory,
    ConsultationHistoryCreate,
    ConsultationHistoryUpdate,
    Campaign,
    CampaignCreate,
    CampaignUpdate,
    CampaignTarget as CampaignTargetSchema,
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


@router.get("/key-metrics")
def get_key_metrics(
    target_month: Optional[str] = None,  # YYYY-MM 형식
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """핵심 지표 조회 - 전월 기준"""
    from models.payment import Payment
    from models.customer import Customer
    from dateutil.relativedelta import relativedelta

    try:
        # 대상 월 설정 (기본값: 전월)
        if target_month:
            target_date = datetime.strptime(target_month + "-01", "%Y-%m-%d").date()
        else:
            today = datetime.now().date()
            target_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)

        # 월의 첫날과 마지막날
        month_start = target_date
        month_end = (target_date + relativedelta(months=1) - timedelta(days=1))

        # 1. 신규 방문상담 수 (전월)
        visit_consult_count = db.query(MarketingLead).filter(
            and_(
                MarketingLead.visit_consult_date >= month_start,
                MarketingLead.visit_consult_date <= month_end,
                MarketingLead.visit_consult_date.isnot(None)
            )
        ).count()

        # 2. 결제 고객 수 (전월 신규 방문상담 중 전환된 고객)
        converted_from_visit = db.query(MarketingLead).filter(
            and_(
                MarketingLead.visit_consult_date >= month_start,
                MarketingLead.visit_consult_date <= month_end,
                MarketingLead.registration_date.isnot(None)
            )
        ).count()

        # 3. 전환율
        conversion_rate = round(converted_from_visit / visit_consult_count * 100, 1) if visit_consult_count > 0 else 0

        # 4. 전월 전체 결제 고객 수 및 매출
        payment_customers = db.query(
            func.count(func.distinct(Payment.customer_id)).label('customer_count'),
            func.sum(Payment.amount).label('total_revenue')
        ).filter(
            and_(
                Payment.payment_date >= month_start,
                Payment.payment_date <= month_end
            )
        ).first()

        total_payment_customers = payment_customers.customer_count or 0
        total_revenue = float(payment_customers.total_revenue or 0)

        # 5. 평균 결제 객단가
        avg_payment_amount = round(total_revenue / total_payment_customers, 0) if total_payment_customers > 0 else 0

        # 월별 추이 (최근 6개월)
        monthly_trends = []
        for i in range(6):
            trend_start = (target_date - relativedelta(months=i)).replace(day=1)
            trend_end = (trend_start + relativedelta(months=1) - timedelta(days=1))

            # 해당 월 방문상담 수
            trend_visits = db.query(MarketingLead).filter(
                and_(
                    MarketingLead.visit_consult_date >= trend_start,
                    MarketingLead.visit_consult_date <= trend_end,
                    MarketingLead.visit_consult_date.isnot(None)
                )
            ).count()

            # 해당 월 전환 수
            trend_conversions = db.query(MarketingLead).filter(
                and_(
                    MarketingLead.visit_consult_date >= trend_start,
                    MarketingLead.visit_consult_date <= trend_end,
                    MarketingLead.registration_date.isnot(None)
                )
            ).count()

            # 해당 월 결제 현황
            trend_payments = db.query(
                func.count(func.distinct(Payment.customer_id)).label('customer_count'),
                func.sum(Payment.amount).label('revenue')
            ).filter(
                and_(
                    Payment.payment_date >= trend_start,
                    Payment.payment_date <= trend_end
                )
            ).first()

            trend_payment_customers = trend_payments.customer_count or 0
            trend_revenue = float(trend_payments.revenue or 0)
            trend_avg_amount = round(trend_revenue / trend_payment_customers, 0) if trend_payment_customers > 0 else 0

            monthly_trends.append({
                "month": trend_start.strftime("%Y-%m"),
                "visit_consults": trend_visits,
                "conversions": trend_conversions,
                "conversion_rate": round(trend_conversions / trend_visits * 100, 1) if trend_visits > 0 else 0,
                "payment_customers": trend_payment_customers,
                "revenue": trend_revenue,
                "avg_payment_amount": trend_avg_amount
            })

        # 주간 추이 (최근 8주)
        weekly_trends = []
        for i in range(8):
            week_start = target_date - timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)

            # 해당 주 방문상담 수
            week_visits = db.query(MarketingLead).filter(
                and_(
                    MarketingLead.visit_consult_date >= week_start,
                    MarketingLead.visit_consult_date <= week_end,
                    MarketingLead.visit_consult_date.isnot(None)
                )
            ).count()

            # 해당 주 전환 수
            week_conversions = db.query(MarketingLead).filter(
                and_(
                    MarketingLead.visit_consult_date >= week_start,
                    MarketingLead.visit_consult_date <= week_end,
                    MarketingLead.registration_date.isnot(None)
                )
            ).count()

            # 해당 주 결제 현황
            week_payments = db.query(
                func.count(func.distinct(Payment.customer_id)).label('customer_count'),
                func.sum(Payment.amount).label('revenue')
            ).filter(
                and_(
                    Payment.payment_date >= week_start,
                    Payment.payment_date <= week_end
                )
            ).first()

            week_payment_customers = week_payments.customer_count or 0
            week_revenue = float(week_payments.revenue or 0)

            weekly_trends.append({
                "week": f"{week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}",
                "visit_consults": week_visits,
                "conversions": week_conversions,
                "conversion_rate": round(week_conversions / week_visits * 100, 1) if week_visits > 0 else 0,
                "payment_customers": week_payment_customers,
                "revenue": week_revenue
            })

        return {
            "target_month": target_date.strftime("%Y년 %m월"),
            "key_metrics": {
                "new_visit_consults": visit_consult_count,
                "converted_customers": converted_from_visit,
                "conversion_rate": conversion_rate,
                "total_payment_customers": total_payment_customers,
                "total_revenue": total_revenue,
                "avg_payment_amount": avg_payment_amount
            },
            "formulas": {
                "formula1": {
                    "description": "신규 방문상담 수 × 전환율 = 결제 고객 수",
                    "calculation": f"{visit_consult_count} × {conversion_rate}% = {converted_from_visit}명",
                    "values": {
                        "visit_consults": visit_consult_count,
                        "conversion_rate": conversion_rate,
                        "result": converted_from_visit
                    }
                },
                "formula2": {
                    "description": "결제 고객 수 × 평균 결제 객단가 = 매출액",
                    "calculation": f"{total_payment_customers}명 × {avg_payment_amount:,}원 = {total_revenue:,}원",
                    "values": {
                        "payment_customers": total_payment_customers,
                        "avg_amount": avg_payment_amount,
                        "result": total_revenue
                    }
                }
            },
            "monthly_trends": list(reversed(monthly_trends)),
            "weekly_trends": list(reversed(weekly_trends))
        }

    except Exception as e:
        print(f"Key metrics error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
def get_lead_analytics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """유입고객 분석 데이터 조회"""
    # 기본 쿼리
    base_query = db.query(MarketingLead)
    if date_from:
        base_query = base_query.filter(MarketingLead.lead_date >= date_from)
    if date_to:
        base_query = base_query.filter(MarketingLead.lead_date <= date_to)

    # 개요 통계
    total_leads = base_query.count()
    converted_leads = base_query.filter(MarketingLead.registration_date.isnot(None)).count()
    active_leads = base_query.filter(
        MarketingLead.registration_date.is_(None),
        or_(
            MarketingLead.phone_consult_date.isnot(None),
            MarketingLead.visit_consult_date.isnot(None)
        )
    ).count()
    lost_leads = base_query.filter(
        MarketingLead.registration_date.is_(None),
        MarketingLead.no_registration_reason.isnot(None)
    ).count()

    # 평균 전환 소요일
    avg_days_result = db.query(
        func.avg(
            MarketingLead.registration_date - MarketingLead.lead_date
        )
    ).filter(
        MarketingLead.registration_date.isnot(None),
        MarketingLead.lead_date.isnot(None)
    )
    if date_from:
        avg_days_result = avg_days_result.filter(MarketingLead.lead_date >= date_from)
    if date_to:
        avg_days_result = avg_days_result.filter(MarketingLead.lead_date <= date_to)

    avg_conversion_days = avg_days_result.scalar() or 0

    # 채널별 성과
    channel_stats = db.query(
        MarketingLead.lead_channel,
        func.count(MarketingLead.lead_id).label('leads'),
        func.count(MarketingLead.registration_date).label('conversions'),
        func.avg(
            MarketingLead.registration_date - MarketingLead.lead_date
        ).label('avg_days')
    )
    if date_from:
        channel_stats = channel_stats.filter(MarketingLead.lead_date >= date_from)
    if date_to:
        channel_stats = channel_stats.filter(MarketingLead.lead_date <= date_to)

    channel_stats = channel_stats.group_by(MarketingLead.lead_channel).all()

    channel_performance = [
        {
            "channel": stat.lead_channel or "미분류",
            "leads": stat.leads,
            "conversions": stat.conversions,
            "conversion_rate": round(stat.conversions / stat.leads * 100, 1) if stat.leads > 0 else 0,
            "avg_days_to_convert": round(stat.avg_days or 0)
        }
        for stat in channel_stats
    ]

    # 월별 트렌드
    monthly_query = db.query(
        func.to_char(MarketingLead.lead_date, 'YYYY-MM').label('month'),
        func.count(MarketingLead.lead_id).label('leads'),
        func.count(MarketingLead.registration_date).label('conversions')
    )
    if date_from:
        monthly_query = monthly_query.filter(MarketingLead.lead_date >= date_from)
    if date_to:
        monthly_query = monthly_query.filter(MarketingLead.lead_date <= date_to)

    monthly_stats = monthly_query.group_by('month').order_by('month').all()

    monthly_trends = [
        {
            "month": stat.month,
            "leads": stat.leads,
            "conversions": stat.conversions,
            "conversion_rate": round(stat.conversions / stat.leads * 100, 1) if stat.leads > 0 else 0
        }
        for stat in monthly_stats
    ]

    # 깔때기 분석
    funnel_query = base_query
    funnel_analysis = {
        "total_leads": funnel_query.count(),
        "db_entered": funnel_query.filter(MarketingLead.db_entry_date.isnot(None)).count(),
        "phone_consulted": funnel_query.filter(MarketingLead.phone_consult_date.isnot(None)).count(),
        "visit_consulted": funnel_query.filter(MarketingLead.visit_consult_date.isnot(None)).count(),
        "converted": funnel_query.filter(MarketingLead.registration_date.isnot(None)).count()
    }

    # 지역별 통계
    regional_stats = db.query(
        MarketingLead.region,
        func.count(MarketingLead.lead_id).label('leads'),
        func.count(MarketingLead.registration_date).label('conversions')
    )
    if date_from:
        regional_stats = regional_stats.filter(MarketingLead.lead_date >= date_from)
    if date_to:
        regional_stats = regional_stats.filter(MarketingLead.lead_date <= date_to)

    regional_stats = regional_stats.group_by(MarketingLead.region).order_by(desc('leads')).all()

    regional_data = [
        {
            "region": stat.region or "미분류",
            "leads": stat.leads,
            "conversion_rate": round(stat.conversions / stat.leads * 100, 1) if stat.leads > 0 else 0
        }
        for stat in regional_stats
    ]

    # 캠페인 성과 (최근 5개)
    recent_campaigns = db.query(ReregistrationCampaign).order_by(
        desc(ReregistrationCampaign.created_at)
    ).limit(5).all()

    campaign_performance = [
        {
            "campaign_name": campaign.campaign_name,
            "targets": campaign.target_count,
            "conversions": campaign.success_count,
            "conversion_rate": round(campaign.success_count / campaign.target_count * 100, 1) if campaign.target_count > 0 else 0,
            "roi": 0  # ROI 계산은 비용 데이터가 필요함
        }
        for campaign in recent_campaigns
    ]

    return {
        "overview": {
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "conversion_rate": round(converted_leads / total_leads * 100, 1) if total_leads > 0 else 0,
            "avg_conversion_days": round(avg_conversion_days),
            "active_leads": active_leads,
            "lost_leads": lost_leads
        },
        "channel_performance": channel_performance,
        "monthly_trends": monthly_trends,
        "funnel_analysis": funnel_analysis,
        "regional_stats": regional_data,
        "campaign_performance": campaign_performance
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
        filename = f"customer_leads_{date.today()}.xlsx"
    else:
        df.to_csv(output, index=False, encoding='utf-8-sig')
        media_type = "text/csv; charset=utf-8"
        filename = f"customer_leads_{date.today()}.csv"

    output.seek(0)

    return StreamingResponse(
        output,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
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
                    value = row[excel_col]
                    # 가격안내 특별 처리
                    if db_col == 'price_informed':
                        lead_data[db_col] = value == '예'
                    else:
                        lead_data[db_col] = value

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


# ========== 캠페인 관련 엔드포인트 ==========

@router.get("/campaigns")
def get_campaigns(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """재등록 캠페인 목록 조회"""
    query = db.query(ReregistrationCampaign).options(
        joinedload(ReregistrationCampaign.created_by_user)
    )

    if is_active is not None:
        query = query.filter(ReregistrationCampaign.is_active == is_active)

    campaigns = query.order_by(desc(ReregistrationCampaign.created_at)).all()

    # 생성자 이름 추가
    for campaign in campaigns:
        if campaign.created_by_user:
            campaign.created_by_name = campaign.created_by_user.name

    return campaigns


@router.get("/campaigns/stats")
def get_campaign_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """캠페인 통계 조회"""
    try:
        total_campaigns = db.query(ReregistrationCampaign).count()
        active_campaigns = db.query(ReregistrationCampaign).filter(
            ReregistrationCampaign.is_active == True
        ).count()

        # 총 대상 인원 및 전환 수
        targets_stats = db.query(
            func.count(CampaignTargetModel.target_id).label('total_targets'),
            func.sum(func.cast(CampaignTargetModel.converted, Integer)).label('total_conversions')
        ).first()

        total_targets = targets_stats.total_targets or 0
        total_conversions = int(targets_stats.total_conversions or 0)

        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_targets": total_targets,
            "total_conversions": total_conversions,
            "overall_conversion_rate": round(total_conversions / total_targets * 100, 1) if total_targets > 0 else 0
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error in get_campaign_stats: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Full traceback:\n{error_detail}")

        # 더 자세한 에러 메시지 반환
        if hasattr(e, 'orig'):
            detail = f"{type(e).__name__}: {str(e.orig)}"
        else:
            detail = f"{type(e).__name__}: {str(e)}"

        raise HTTPException(status_code=500, detail=detail)


@router.post("/campaigns")
def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """재등록 캠페인 생성"""
    db_campaign = ReregistrationCampaign(
        **campaign.dict(),
        created_by=current_user.user_id
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)

    # 대상 고객 자동 추가 (target_criteria 기반)
    if campaign.target_criteria:
        criteria = campaign.target_criteria
        query = db.query(MarketingLead)

        # 마지막 서비스 이용일 기준
        if criteria.get('days_since_last_service'):
            cutoff_date = date.today() - timedelta(days=criteria['days_since_last_service'])
            query = query.filter(
                or_(
                    MarketingLead.last_service_date <= cutoff_date,
                    MarketingLead.last_service_date.is_(None)
                )
            )

        # 미등록 고객 포함 여부
        if not criteria.get('include_no_registration', True):
            query = query.filter(MarketingLead.registration_date.isnot(None))

        # 재등록 대상으로 표시된 고객만
        query = query.filter(MarketingLead.is_reregistration_target == True)

        leads = query.all()

        # 캠페인 대상으로 추가
        for lead in leads:
            target = CampaignTargetModel(
                campaign_id=db_campaign.campaign_id,
                lead_id=lead.lead_id
            )
            db.add(target)

        db_campaign.target_count = len(leads)
        db.commit()

    db_campaign.created_by_name = current_user.name
    return db_campaign


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


@router.put("/{lead_id}/consultations/{consultation_id}")
def update_consultation_history(
    lead_id: int,
    consultation_id: int,
    consultation_update: ConsultationHistoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """상담 이력 수정"""
    # 상담 이력 확인
    consultation = db.query(LeadConsultationHistory).filter(
        LeadConsultationHistory.consultation_id == consultation_id,
        LeadConsultationHistory.lead_id == lead_id
    ).first()

    if not consultation:
        raise HTTPException(status_code=404, detail="상담 이력을 찾을 수 없습니다")

    # 업데이트
    update_data = consultation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(consultation, field, value)

    consultation.updated_at = datetime.now()
    db.commit()
    db.refresh(consultation)

    # 생성자 정보 추가
    if consultation.created_by:
        creator = db.query(User).filter(User.user_id == consultation.created_by).first()
        if creator:
            consultation.created_by_name = creator.name

    return consultation


@router.delete("/{lead_id}/consultations/{consultation_id}")
def delete_consultation_history(
    lead_id: int,
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """상담 이력 삭제"""
    # 상담 이력 확인
    consultation = db.query(LeadConsultationHistory).filter(
        LeadConsultationHistory.consultation_id == consultation_id,
        LeadConsultationHistory.lead_id == lead_id
    ).first()

    if not consultation:
        raise HTTPException(status_code=404, detail="상담 이력을 찾을 수 없습니다")

    db.delete(consultation)
    db.commit()

    return {"message": "상담 이력이 삭제되었습니다"}


@router.get("/campaigns/{campaign_id}")
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """캠페인 상세 조회"""
    campaign = db.query(ReregistrationCampaign).options(
        joinedload(ReregistrationCampaign.created_by_user)
    ).filter(ReregistrationCampaign.campaign_id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="캠페인을 찾을 수 없습니다")

    if campaign.created_by_user:
        campaign.created_by_name = campaign.created_by_user.name

    return campaign


@router.put("/campaigns/{campaign_id}")
def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """캠페인 수정"""
    db_campaign = db.query(ReregistrationCampaign).filter(
        ReregistrationCampaign.campaign_id == campaign_id
    ).first()

    if not db_campaign:
        raise HTTPException(status_code=404, detail="캠페인을 찾을 수 없습니다")

    update_data = campaign_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_campaign, field, value)

    db_campaign.updated_at = datetime.now()
    db.commit()
    db.refresh(db_campaign)

    return db_campaign


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """캠페인 삭제"""
    db_campaign = db.query(ReregistrationCampaign).filter(
        ReregistrationCampaign.campaign_id == campaign_id
    ).first()

    if not db_campaign:
        raise HTTPException(status_code=404, detail="캠페인을 찾을 수 없습니다")

    # 관련 대상도 삭제 (CASCADE 설정이 없는 경우)
    db.query(CampaignTargetModel).filter(
        CampaignTargetModel.campaign_id == campaign_id
    ).delete()

    db.delete(db_campaign)
    db.commit()

    return {"message": "캠페인이 삭제되었습니다"}


@router.get("/campaigns/{campaign_id}/targets")
def get_campaign_targets(
    campaign_id: int,
    converted: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """캠페인 대상 고객 목록 조회"""
    query = db.query(CampaignTargetModel).options(
        joinedload(CampaignTargetModel.lead)
    ).filter(CampaignTargetModel.campaign_id == campaign_id)

    if converted is not None:
        query = query.filter(CampaignTargetModel.converted == converted)

    targets = query.order_by(CampaignTargetModel.created_at).all()

    # 리드 정보 추가
    for target in targets:
        if target.lead:
            target.lead_name = target.lead.name
            target.lead_phone = target.lead.phone

    return targets


@router.put("/campaigns/{campaign_id}/targets/{target_id}")
def update_campaign_target(
    campaign_id: int,
    target_id: int,
    contact_date: Optional[date] = None,
    contact_result: Optional[str] = None,
    converted: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """캠페인 대상 고객 업데이트"""
    target = db.query(CampaignTargetModel).filter(
        CampaignTargetModel.target_id == target_id,
        CampaignTargetModel.campaign_id == campaign_id
    ).first()

    if not target:
        raise HTTPException(status_code=404, detail="대상 고객을 찾을 수 없습니다")

    if contact_date:
        target.contact_date = contact_date
    if contact_result:
        target.contact_result = contact_result
    if converted is not None:
        target.converted = converted

        # 캠페인 성공 수 업데이트
        if converted:
            campaign = db.query(ReregistrationCampaign).filter(
                ReregistrationCampaign.campaign_id == campaign_id
            ).first()
            if campaign:
                campaign.success_count = db.query(CampaignTargetModel).filter(
                    CampaignTargetModel.campaign_id == campaign_id,
                    CampaignTargetModel.converted == True
                ).count()

    db.commit()
    db.refresh(target)

    return target
