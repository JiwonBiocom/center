"""
고객 관리 확장 API 엔드포인트
- 고객 상세 정보 조회
- 고객 분석 데이터 조회
- 서비스 추천 조회
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from core.database import get_db
from core.auth import get_current_user
from schemas.customer import CustomerDetail
from models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/customers",
    tags=["customers-extended"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/{customer_id}/detail", response_model=Dict[str, Any])
async def get_customer_detail(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 상세 정보 조회 (확장)"""
    logger.info(f"Getting customer detail for customer_id: {customer_id}")
    
    try:
        # 1. 고객 기본 정보 조회
        customer_query = text("""
        SELECT 
            c.customer_id,
            c.name,
            c.phone,
            c.email,
            c.first_visit_date,
            c.region,
            c.referral_source,
            c.health_concerns,
            c.notes,
            c.assigned_staff,
            c.birth_year,
            c.gender,
            c.address,
            c.emergency_contact,
            c.occupation,
            c.membership_level,
            c.customer_status,
            c.preferred_time_slots,
            c.health_goals,
            c.last_visit_date,
            c.total_visits,
            c.average_visit_interval,
            c.total_revenue,
            c.average_satisfaction,
            c.created_at,
            c.updated_at
        FROM customers c
        WHERE c.customer_id = :customer_id
        """)
        
        customer = db.execute(customer_query, {"customer_id": customer_id}).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="고객을 찾을 수 없습니다"
            )
        
        # 2. 서비스 이용 내역 조회
        service_history_query = text("""
        SELECT 
            su.usage_id as session_id,
            su.service_date,
            st.service_name,
            st.service_type_id,
            st.default_duration as duration_minutes,
            su.session_number,
            su.session_details as session_notes,
            p.package_name,
            u.name as staff_name,
            -- 만족도는 임시로 NULL (향후 추가 예정)
            NULL as satisfaction_rating
        FROM service_usage su
        JOIN service_types st ON su.service_type_id = st.service_type_id
        LEFT JOIN packages p ON su.package_id = p.package_id
        LEFT JOIN users u ON su.created_by = CAST(u.user_id AS VARCHAR)
        WHERE su.customer_id = :customer_id
        ORDER BY su.service_date DESC
        LIMIT 50
        """)
        
        service_history = db.execute(service_history_query, {"customer_id": customer_id}).all()
        
        # 3. 활성 패키지 정보 조회
        active_packages_query = text("""
        SELECT 
            pp.purchase_id as package_usage_id,
            p.package_name,
            pp.purchase_date,
            pp.expiry_date,
            p.total_sessions,
            pp.remaining_sessions,
            pp.used_sessions,
            CASE 
                WHEN p.total_sessions > 0 
                THEN ROUND((pp.used_sessions::numeric / p.total_sessions::numeric) * 100, 1)
                ELSE 0 
            END as usage_rate,
            pp.expiry_date - CURRENT_DATE as days_remaining,
            CASE 
                WHEN pp.expiry_date >= CURRENT_DATE AND pp.remaining_sessions > 0 THEN 'active'
                WHEN pp.expiry_date < CURRENT_DATE THEN 'expired'
                WHEN pp.remaining_sessions = 0 THEN 'completed'
                ELSE 'unknown'
            END as status
        FROM package_purchases pp
        JOIN packages p ON pp.package_id = p.package_id
        WHERE pp.customer_id = :customer_id
            AND pp.expiry_date >= CURRENT_DATE
            AND pp.remaining_sessions > 0
        ORDER BY pp.purchase_date DESC
        """)
        
        active_packages = db.execute(active_packages_query, {"customer_id": customer_id}).all()
        
        # 4. 고객 선호도 조회
        preferences_query = text("""
        SELECT 
            preferred_services,
            preferred_time,
            preferred_intensity,
            health_interests,
            communication_preference,
            marketing_consent
        FROM customer_preferences
        WHERE customer_id = :customer_id
        """)
        
        preferences = db.execute(preferences_query, {"customer_id": customer_id}).first()
        
        # 5. 서비스 이용 통계 생성
        service_stats_query = text("""
        SELECT 
            st.service_type_id,
            st.service_name,
            COUNT(*) as usage_count
        FROM service_usage su
        JOIN service_types st ON su.service_type_id = st.service_type_id
        WHERE su.customer_id = :customer_id
        GROUP BY st.service_type_id, st.service_name
        ORDER BY usage_count DESC
        """)
        
        service_stats = db.execute(service_stats_query, {"customer_id": customer_id}).all()
        
        # 6. 인바디 정보 조회 (최근 5개 기록)
        inbody_query = text("""
        SELECT 
            record_id,
            measurement_date,
            weight,
            body_fat_percentage,
            skeletal_muscle_mass,
            extracellular_water_ratio,
            phase_angle,
            visceral_fat_level,
            notes,
            measured_by,
            created_at,
            updated_at
        FROM inbody_records
        WHERE customer_id = :customer_id
        ORDER BY measurement_date DESC
        LIMIT 5
        """)
        
        inbody_records = db.execute(inbody_query, {"customer_id": customer_id}).all()
        
        # 결과 포맷팅
        logger.info(f"Building result for customer_id: {customer_id})")
        result = {
            "customer": {
                "customer_id": customer.customer_id,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "first_visit_date": customer.first_visit_date.isoformat() if customer.first_visit_date else None,
                "region": customer.region,
                "referral_source": customer.referral_source,
                "health_concerns": customer.health_concerns,
                "notes": customer.notes,
                "assigned_staff": customer.assigned_staff,
                "birth_year": customer.birth_year,
                "gender": customer.gender,
                "address": customer.address,
                "emergency_contact": customer.emergency_contact,
                "occupation": customer.occupation,
                "membership_level": customer.membership_level,
                "customer_status": customer.customer_status,
                "preferred_time_slots": customer.preferred_time_slots,
                "health_goals": customer.health_goals,
                "last_visit_date": customer.last_visit_date.isoformat() if customer.last_visit_date else None,
                "total_visits": customer.total_visits,
                "average_visit_interval": customer.average_visit_interval,
                "total_revenue": float(customer.total_revenue) if customer.total_revenue else 0,
                "average_satisfaction": float(customer.average_satisfaction) if customer.average_satisfaction else None,
                "created_at": customer.created_at.isoformat() if customer.created_at else None,
                "updated_at": customer.updated_at.isoformat() if customer.updated_at else None
            },
        "serviceHistory": [
            {
                "session_id": row.session_id,
                "service_date": row.service_date.isoformat() if row.service_date else None,
                "service_type_id": row.service_type_id,
                "service_name": row.service_name,
                "duration_minutes": row.duration_minutes,
                "satisfaction_rating": row.satisfaction_rating,
                "session_notes": row.session_notes,
                "staff_name": row.staff_name,
                "package_name": row.package_name
            }
            for row in service_history
        ],
        "activePackages": [
            {
                "package_usage_id": row.package_usage_id,
                "package_name": row.package_name,
                "purchase_date": row.purchase_date.isoformat() if row.purchase_date else None,
                "expiry_date": row.expiry_date.isoformat() if row.expiry_date else None,
                "total_sessions": row.total_sessions,
                "used_sessions": row.used_sessions,
                "remaining_sessions": row.remaining_sessions,
                "usage_rate": float(row.usage_rate) if row.usage_rate else 0,
                "days_remaining": row.days_remaining,
                "status": row.status,
                "service_breakdown": {}  # TODO: 서비스별 세부 사용 내역 추가
            }
            for row in active_packages
        ],
        "preferences": {
            "preferred_services": preferences.preferred_services if preferences else [],
            "preferred_time": preferences.preferred_time if preferences else None,
            "preferred_intensity": preferences.preferred_intensity if preferences else None,
            "health_interests": preferences.health_interests if preferences else [],
            "communication_preference": preferences.communication_preference if preferences else None,
            "marketing_consent": preferences.marketing_consent if preferences else False
        } if preferences else None,
        "serviceUsageSummary": {
            f"service_{service.service_type_id}": {
                "name": service.service_name,
                "count": service.usage_count
            }
            for service in service_stats
        },
        "inbodyRecords": [
            {
                "record_id": record.record_id,
                "measurement_date": record.measurement_date.isoformat() if record.measurement_date else None,
                "weight": float(record.weight) if record.weight else None,
                "body_fat_percentage": float(record.body_fat_percentage) if record.body_fat_percentage else None,
                "skeletal_muscle_mass": float(record.skeletal_muscle_mass) if record.skeletal_muscle_mass else None,
                "extracellular_water_ratio": float(record.extracellular_water_ratio) if record.extracellular_water_ratio else None,
                "phase_angle": float(record.phase_angle) if record.phase_angle else None,
                "visceral_fat_level": record.visceral_fat_level,
                "notes": record.notes,
                "measured_by": record.measured_by,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "updated_at": record.updated_at.isoformat() if record.updated_at else None
            }
            for record in inbody_records
        ]
    }
    
        
        logger.info(f"Successfully built result for customer_id: {customer_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_customer_detail: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting customer detail: {str(e)}"
        )

@router.put("/{customer_id}/detail")
async def update_customer_detail(
    customer_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 상세 정보 업데이트"""
    
    # 고객 존재 확인
    customer_exists = db.execute(
        text("SELECT 1 FROM customers WHERE customer_id = :customer_id"),
        {"customer_id": customer_id}
    ).first()
    
    if not customer_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="고객을 찾을 수 없습니다"
        )
    
    # 업데이트 가능한 필드 정의
    allowed_fields = [
        'email', 'birth_year', 'gender', 'address', 'emergency_contact',
        'occupation', 'membership_level', 'health_goals', 'notes'
    ]
    
    # 업데이트할 필드 필터링
    update_fields = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
    
    if update_fields:
        # 업데이트 쿼리 생성
        set_clause = ', '.join([f"{k} = :{k}" for k in update_fields.keys()])
        update_fields['customer_id'] = customer_id
        
        query = text(f"""
            UPDATE customers 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE customer_id = :customer_id
        """)
        
        db.execute(query, update_fields)
        db.commit()
    
    # 선호도 업데이트 (있는 경우)
    if 'preferences' in data and data['preferences']:
        pref_data = data['preferences']
        
        # 기존 선호도 확인
        existing = db.execute(
            text("SELECT preference_id FROM customer_preferences WHERE customer_id = :customer_id"),
            {"customer_id": customer_id}
        ).first()
        
        pref_fields = {
            'customer_id': customer_id,
            'preferred_services': pref_data.get('preferred_services'),
            'preferred_time': pref_data.get('preferred_time'),
            'preferred_intensity': pref_data.get('preferred_intensity'),
            'health_interests': pref_data.get('health_interests'),
            'communication_preference': pref_data.get('communication_preference'),
            'marketing_consent': pref_data.get('marketing_consent', False)
        }
        
        # NULL 값 제거
        pref_fields = {k: v for k, v in pref_fields.items() if v is not None}
        
        if existing:
            # 업데이트
            if len(pref_fields) > 1:  # customer_id 외에 업데이트할 필드가 있는 경우
                set_clause = ', '.join([f"{k} = :{k}" for k in pref_fields.keys() if k != 'customer_id'])
                query = text(f"""
                    UPDATE customer_preferences 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE customer_id = :customer_id
                """)
                db.execute(query, pref_fields)
        else:
            # 새로 생성
            columns = ', '.join(pref_fields.keys())
            values = ', '.join([f":{k}" for k in pref_fields.keys()])
            query = text(f"""
                INSERT INTO customer_preferences ({columns}, created_at, updated_at)
                VALUES ({values}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            db.execute(query, pref_fields)
        
        db.commit()
    
    return {"message": "고객 정보가 업데이트되었습니다"}

@router.get("/{customer_id}/service-history")
async def get_service_history(
    customer_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 서비스 이용 내역 조회 (페이지네이션)"""
    
    query = text("""
        SELECT 
            su.usage_id,
            su.service_date,
            st.service_name,
            st.service_type_id,
            st.default_duration as duration_minutes,
            su.session_number,
            su.session_details,
            p.package_name,
            u.name as staff_name
        FROM service_usage su
        JOIN service_types st ON su.service_type_id = st.service_type_id
        LEFT JOIN packages p ON su.package_id = p.package_id
        LEFT JOIN users u ON su.created_by = CAST(u.user_id AS VARCHAR)
        WHERE su.customer_id = :customer_id
        ORDER BY su.service_date DESC
        LIMIT :limit OFFSET :offset
    """)
    
    results = db.execute(query, {
        "customer_id": customer_id,
        "limit": limit,
        "offset": offset
    }).all()
    
    # 전체 개수 조회
    count_query = text("""
        SELECT COUNT(*) FROM service_usage WHERE customer_id = :customer_id
    """)
    total_count = db.execute(count_query, {"customer_id": customer_id}).scalar()
    
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "data": [
            {
                "usage_id": row.usage_id,
                "service_date": row.service_date.isoformat() if row.service_date else None,
                "service_name": row.service_name,
                "service_type_id": row.service_type_id,
                "duration_minutes": row.duration_minutes,
                "session_number": row.session_number,
                "session_details": row.session_details,
                "package_name": row.package_name,
                "staff_name": row.staff_name
            }
            for row in results
        ]
    }

@router.get("/{customer_id}/analytics")
async def get_customer_analytics(
    customer_id: int,
    period: str = "90d",  # 30d, 90d, 180d, 1y, 6months
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 분석 데이터 조회"""
    
    try:
        logger.info(f"Getting analytics for customer {customer_id}, period: {period}")
        
        # 기간 계산
        period_days = {
            "30d": 30,
            "90d": 90,
            "180d": 180,
            "6months": 180,
            "1y": 365
        }.get(period, 90)
        
        logger.info(f"Period days calculated: {period_days}")
        
        # 월별 방문 횟수
        monthly_visits_query = text(f"""
            SELECT 
                TO_CHAR(service_date, 'YYYY-MM') as month,
                COUNT(*) as visits
            FROM service_usage
            WHERE customer_id = :customer_id
                AND service_date >= CURRENT_DATE - INTERVAL '{period_days} days'
            GROUP BY TO_CHAR(service_date, 'YYYY-MM')
            ORDER BY month
        """)
        
        monthly_visits = db.execute(monthly_visits_query, {
            "customer_id": customer_id
        }).all()
        
        # 2. 서비스 이용 분석
        service_usage_query = text(f"""
            SELECT 
                st.service_type_id,
                st.service_name,
                COUNT(*) as usage_count,
                AVG(CASE 
                    WHEN su.session_number IS NOT NULL 
                    THEN su.session_number 
                    ELSE 0 
                END) as avg_session_number
            FROM service_usage su
            JOIN service_types st ON su.service_type_id = st.service_type_id
            WHERE su.customer_id = :customer_id
                AND su.service_date >= CURRENT_DATE - INTERVAL '{period_days} days'
            GROUP BY st.service_type_id, st.service_name
            ORDER BY usage_count DESC
        """)
        
        service_usage = db.execute(service_usage_query, {
            "customer_id": customer_id
        }).all()
        
        # 서비스별 분포 계산
        total_services = sum(row.usage_count for row in service_usage)
        service_distribution = {}
        if total_services > 0:
            for row in service_usage:
                service_distribution[f"service_{row.service_type_id}"] = round((row.usage_count / total_services) * 100, 1)
        
        # 3. 수익 기여도 분석
        revenue_query = text(f"""
            SELECT 
                COALESCE(SUM(amount), 0) as total_revenue,
                COUNT(*) as payment_count,
                AVG(amount) as avg_payment,
                TO_CHAR(payment_date, 'YYYY-MM') as month,
                SUM(amount) as monthly_revenue
            FROM payments
            WHERE customer_id = :customer_id
                AND payment_date >= CURRENT_DATE - INTERVAL '{period_days} days'
            GROUP BY TO_CHAR(payment_date, 'YYYY-MM')
            ORDER BY month
        """)
        
        revenue_data = db.execute(revenue_query, {
            "customer_id": customer_id
        }).all()
        
        # 전체 수익 통계
        total_revenue_query = text(f"""
            SELECT 
                COALESCE(SUM(amount), 0) as total_revenue,
                COUNT(*) as payment_count,
                AVG(amount) as avg_payment
            FROM payments
            WHERE customer_id = :customer_id
                AND payment_date >= CURRENT_DATE - INTERVAL '{period_days} days'
        """)
        
        revenue_stats = db.execute(total_revenue_query, {
            "customer_id": customer_id
        }).first()
        
        # 4. 위험도 평가
        # 최근 방문일 확인
        last_visit_query = text("""
            SELECT 
                MAX(service_date) as last_visit,
                CURRENT_DATE - MAX(service_date) as days_since_last_visit
            FROM service_usage
            WHERE customer_id = :customer_id
        """)
        
        last_visit = db.execute(last_visit_query, {"customer_id": customer_id}).first()
        
        # 위험도 계산
        days_since = last_visit.days_since_last_visit if last_visit and last_visit.days_since_last_visit else 999
        if days_since < 30:
            churn_risk = "low"
            churn_probability = 10
        elif days_since < 60:
            churn_risk = "medium"
            churn_probability = 30
        elif days_since < 90:
            churn_risk = "high"
            churn_probability = 60
        else:
            churn_risk = "very_high"
            churn_probability = 85
        
        # 방문 기본 정보 조회
        basic_info_query = text("""
            SELECT 
                COUNT(DISTINCT service_date) as total_visits,
                MIN(service_date) as first_visit,
                MAX(service_date) as last_visit,
                COUNT(DISTINCT TO_CHAR(service_date, 'YYYY-MM')) as active_months
            FROM service_usage
            WHERE customer_id = :customer_id
        """)
        
        basic_info = db.execute(basic_info_query, {"customer_id": customer_id}).first()
        
        # 평균 방문 주기 계산
        if basic_info and basic_info.total_visits > 1:
            days_between = (basic_info.last_visit - basic_info.first_visit).days
            avg_interval = days_between / (basic_info.total_visits - 1) if basic_info.total_visits > 1 else 0
        else:
            avg_interval = 0
        
        # 서비스별 카운트
        service_counts = {}
        most_used_service = None
        total_sessions = 0
        
        if service_usage:
            for row in service_usage:
                service_counts[row.service_name] = row.usage_count
                total_sessions += row.usage_count
            most_used_service = service_usage[0].service_name
        
        # 선호 시간대/요일 분석 (간단 버전) - service_date가 DATE이므로 시간 정보 없음
        preferred_time = "정보 없음"  # TODO: 향후 TIMESTAMP 컬럼 추가 시 구현
        
        # 요일 패턴
        day_pattern_query = text("""
            SELECT 
                CASE EXTRACT(DOW FROM service_date)
                    WHEN 0 THEN '일요일'
                    WHEN 1 THEN '월요일'
                    WHEN 2 THEN '화요일'
                    WHEN 3 THEN '수요일'
                    WHEN 4 THEN '목요일'
                    WHEN 5 THEN '금요일'
                    WHEN 6 THEN '토요일'
                END as day_name,
                COUNT(*) as count
            FROM service_usage
            WHERE customer_id = :customer_id
            GROUP BY EXTRACT(DOW FROM service_date)
            ORDER BY count DESC
            LIMIT 1
        """)
        
        preferred_day_result = db.execute(day_pattern_query, {"customer_id": customer_id}).first()
        preferred_day = preferred_day_result.day_name if preferred_day_result else "정보 없음"
        
        # 예약 취소율 및 노쇼율 계산
        reservation_stats_query = text(f"""
            SELECT 
                COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled_count,
                COUNT(*) FILTER (WHERE status = 'no_show') as no_show_count,
                COUNT(*) as total_reservations
            FROM reservations
            WHERE customer_id = :customer_id
                AND reservation_date >= CURRENT_DATE - INTERVAL '{period_days} days'
        """)
        
        reservation_stats = db.execute(reservation_stats_query, {"customer_id": customer_id}).first()
        
        cancellation_rate = 0
        no_show_rate = 0
        
        if reservation_stats and reservation_stats.total_reservations > 0:
            cancellation_rate = (reservation_stats.cancelled_count / reservation_stats.total_reservations) * 100
            no_show_rate = (reservation_stats.no_show_count / reservation_stats.total_reservations) * 100
        
        # 월별 매출 데이터
        revenue_by_month = []
        total_revenue = 0
        
        if revenue_data:
            for row in revenue_data:
                revenue_by_month.append({
                    "month": row.month,
                    "revenue": float(row.monthly_revenue)
                })
                total_revenue += float(row.monthly_revenue)
        
        # 결과 포맷팅 (프론트엔드 인터페이스에 맞춤)
        # 1970-01-01 같은 기본값은 None으로 처리
        first_visit = None
        last_visit = None
        
        if basic_info and basic_info.first_visit:
            if basic_info.first_visit.year > 1970:
                first_visit = basic_info.first_visit.isoformat()
        
        if basic_info and basic_info.last_visit:
            if basic_info.last_visit.year > 1970:
                last_visit = basic_info.last_visit.isoformat()
        
        result = {
            "visit_summary": {
                "total_visits": basic_info.total_visits if basic_info else 0,
                "first_visit": first_visit,
                "last_visit": last_visit,
                "visit_frequency": basic_info.total_visits if basic_info else 0,
                "average_interval_days": int(avg_interval) if avg_interval > 0 else 0
            },
            "service_summary": {
                "most_used_service": most_used_service or "정보 없음",
                "service_counts": service_counts,
                "total_sessions": total_sessions
            },
            "revenue_summary": {
                "total_revenue": total_revenue,
                "average_per_visit": total_revenue / basic_info.total_visits if basic_info and basic_info.total_visits > 0 else 0,
                "revenue_by_month": revenue_by_month
            },
            "patterns": {
                "preferred_time": preferred_time,
                "preferred_day": preferred_day,
                "cancellation_rate": round(cancellation_rate, 1),
                "no_show_rate": round(no_show_rate, 1)
            }
        }
        
        logger.info(f"Analytics result prepared for customer {customer_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_customer_analytics for customer {customer_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting customer analytics: {str(e)}"
        )

@router.get("/{customer_id}/recommendations")
async def get_customer_recommendations(
    customer_id: int,
    recommendation_type: str = "all",  # service, package, schedule, all
    count: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객 맞춤 서비스 추천 - 건강설문과 인바디 데이터 기반"""
    
    from models.questionnaire import QuestionnaireResponse, Answer, Question
    from models.inbody import InBodyRecord
    from models.customer import Customer
    import json
    
    recommendations = []
    
    # 고객 정보 가져오기
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="고객을 찾을 수 없습니다"
        )
    
    # 건강설문 데이터 확인
    latest_questionnaire = db.query(QuestionnaireResponse)\
        .filter(QuestionnaireResponse.customer_id == customer_id)\
        .filter(QuestionnaireResponse.is_completed == True)\
        .order_by(QuestionnaireResponse.completed_at.desc())\
        .first()
    
    # 최신 인바디 데이터 확인
    latest_inbody = db.query(InBodyRecord)\
        .filter(InBodyRecord.customer_id == customer_id)\
        .order_by(InBodyRecord.measurement_date.desc())\
        .first()
    
    # 건강설문이 없는 경우 기본 메시지 반환
    if not latest_questionnaire and not latest_inbody:
        return {
            "has_health_data": False,
            "message": "건강 설문과 인바디970 정보를 바탕으로 AI가 맞춤 관리해 드립니다. 정보를 채워주세요",
            "service_recommendations": [],
            "package_recommendations": [],
            "care_recommendations": []
        }
    
    # 1. 고객 서비스 이용 패턴 분석
    usage_pattern_query = text("""
        SELECT 
            st.service_type_id,
            COUNT(*) as usage_count
        FROM service_usage su
        JOIN service_types st ON su.service_type_id = st.service_type_id
        WHERE su.customer_id = :customer_id
        GROUP BY st.service_type_id
        ORDER BY usage_count DESC
    """)
    
    usage_pattern = db.execute(usage_pattern_query, {"customer_id": customer_id}).all()
    used_services = {row.service_type_id for row in usage_pattern}
    
    # 2. 미사용 서비스 추천
    if recommendation_type in ["service", "all"]:
        # Get all available services from database
        all_services_query = text("""
            SELECT service_type_id, service_name 
            FROM service_types
        """)
        all_services_result = db.execute(all_services_query).all()
        all_service_ids = {row.service_type_id for row in all_services_result}
        service_id_to_name = {row.service_type_id: row.service_name for row in all_services_result}
        
        unused_service_ids = [sid for sid in all_service_ids if sid not in used_services]
        
        for service_id in unused_service_ids[:2]:  # 최대 2개 추천
            recommendations.append({
                "type": "service",
                "recommendation_id": f"rec_srv_{service_id}",
                "service_type_id": service_id,
                "service_name": service_id_to_name.get(service_id, f"Service {service_id}"),
                "confidence_score": 0.85,
                "reason": "아직 체험하지 않은 서비스입니다",
                "expected_benefit": f"{service_id_to_name.get(service_id)} 서비스로 새로운 건강 관리를 시작해보세요",
                "suggested_schedule": {
                    "frequency": "주 1회",
                    "duration": "30분",
                    "best_times": ["평일 오전", "주말 오후"]
                }
            })
    
    # 3. 패키지 추천
    if recommendation_type in ["package", "all"]:
        # 현재 활성 패키지 확인
        active_package_query = text("""
            SELECT package_id, expiry_date
            FROM package_purchases
            WHERE customer_id = :customer_id
                AND expiry_date >= CURRENT_DATE
                AND remaining_sessions > 0
            ORDER BY expiry_date DESC
            LIMIT 1
        """)
        
        active_package = db.execute(active_package_query, {"customer_id": customer_id}).first()
        
        if not active_package or (active_package.expiry_date - date.today()).days < 30:
            # 패키지 갱신 추천
            recommendations.append({
                "type": "package",
                "recommendation_id": "rec_pkg_renewal",
                "package_name": "프리미엄 케어 패키지",
                "confidence_score": 0.92,
                "reason": "패키지 만료가 임박했습니다" if active_package else "현재 활성 패키지가 없습니다",
                "package_details": {
                    "brain": 10,
                    "pulse": 10,
                    "lymph": 5,
                    "total_sessions": 25,
                    "price": 1500000,
                    "savings": 250000
                },
                "personalization": {
                    "based_on": "최근 이용 패턴",
                    "optimization": "자주 이용하시는 서비스 중심 구성"
                }
            })
    
    # 4. 스케줄 추천
    if recommendation_type in ["schedule", "all"]:
        recommendations.append({
            "type": "schedule",
            "recommendation_id": "rec_sch_weekly",
            "schedule_name": "주간 최적 스케줄",
            "confidence_score": 0.78,
            "weekly_plan": [
                {
                    "day": "Monday",
                    "time": "10:00",
                    "service_type_id": 1,  # TODO: Get actual service_type_id
                    "duration": 40,
                    "reason": "주 시작 집중력 향상"
                },
                {
                    "day": "Thursday",
                    "time": "14:00",
                    "service_type_id": 2,  # TODO: Get actual service_type_id
                    "duration": 30,
                    "reason": "중간 피로 회복"
                }
            ]
        })
    
    # 프론트엔드 형식에 맞게 변환
    service_recommendations = []
    package_recommendations = []
    care_recommendations = []
    
    for rec in recommendations[:count]:
        if rec["type"] == "service":
            service_recommendations.append({
                "service_name": rec["service_name"],
                "reason": rec["reason"],
                "expected_benefit": rec["expected_benefit"],
                "priority": "medium"  # 기본값
            })
        elif rec["type"] == "package":
            package_recommendations.append({
                "package_name": rec["package_name"],
                "services_included": list(rec["package_details"].keys()) if "package_details" in rec else [],
                "discount_rate": 15,  # 기본 할인율
                "recommended_price": rec["package_details"]["price"] if "package_details" in rec and "price" in rec["package_details"] else 0,
                "reason": rec["reason"]
            })
        elif rec["type"] == "schedule":
            care_recommendations.append({
                "category": "스케줄 관리",
                "suggestion": "주 2회 정기 방문을 추천드립니다",
                "urgency": "soon"
            })
    
    # 기본 추천 추가 (데이터가 없는 경우)
    if not service_recommendations:
        service_recommendations.append({
            "service_name": "브레인 케어",
            "reason": "스트레스 관리와 집중력 향상에 도움",
            "expected_benefit": "정신적 피로 감소 및 업무 효율 증가",
            "priority": "high"
        })
    
    if not care_recommendations:
        care_recommendations.append({
            "category": "건강 관리",
            "suggestion": "정기적인 서비스 이용으로 건강을 유지하세요",
            "urgency": "long-term"
        })
    
    # 건강설문 데이터가 있는 경우 AI 분석 추가
    visit_purpose_answer = None
    purposes = []
    
    if latest_questionnaire:
        # 건강설문 답변 분석
        answers = db.query(Answer)\
            .join(Question, Answer.question_id == Question.question_id)\
            .filter(Answer.response_id == latest_questionnaire.response_id)\
            .all()
        
        # 방문 목적 분석
        visit_purpose_answer = next((a for a in answers if a.question.question_code == "GOALS_001"), None)
        if visit_purpose_answer and visit_purpose_answer.answer_json:
            purposes = visit_purpose_answer.answer_json.get("selected", [])
            
            # 목적별 서비스 추천
            if "weight_loss" in purposes:
                service_recommendations.insert(0, {
                    "service_name": "체중관리 프로그램",
                    "reason": "체중 감량이 목표라고 응답하셨습니다. 전문 영양 상담과 운동 지도를 통해 건강한 다이어트를 도와드립니다.",
                    "expected_benefit": "3개월 내 체중 5-10% 감량 및 체지방률 개선",
                    "priority": "high"
                })
                
            if "muscle_gain" in purposes:
                service_recommendations.insert(0, {
                    "service_name": "근육 증진 프로그램",
                    "reason": "근육 증가가 목표라고 응답하셨습니다. 맞춤형 운동 프로그램과 영양 관리를 제공합니다.",
                    "expected_benefit": "근육량 증가 및 기초대사율 향상",
                    "priority": "high"
                })
                
            if "stress" in purposes:
                service_recommendations.insert(0, {
                    "service_name": "스트레스 관리 프로그램",
                    "reason": "스트레스 관리가 필요하다고 응답하셨습니다. 명상과 이완 요법을 통해 정신 건강을 개선합니다.",
                    "expected_benefit": "스트레스 수준 감소 및 수면의 질 향상",
                    "priority": "high"
                })
        
        # 스트레스 수준 분석
        stress_answer = next((a for a in answers if "스트레스" in a.question.question_text), None)
        if stress_answer and stress_answer.answer_number and stress_answer.answer_number >= 7:
            care_recommendations.insert(0, {
                "category": "스트레스 관리",
                "suggestion": "높은 스트레스 수준이 감지되었습니다. 주 2회 이상 스트레스 완화 프로그램 참여를 권장합니다.",
                "urgency": "immediate"
            })
        
        # 통증 부위 분석
        pain_answer = next((a for a in answers if "뻐근" in a.question.question_text or "아픈" in a.question.question_text), None)
        if pain_answer and pain_answer.answer_value:
            pain_areas = pain_answer.answer_value.lower()
            if "허리" in pain_areas:
                service_recommendations.append({
                    "service_name": "척추 교정 프로그램",
                    "reason": "허리 통증을 호소하셨습니다. 전문 치료사의 맞춤 관리가 필요합니다.",
                    "expected_benefit": "허리 통증 완화 및 자세 개선",
                    "priority": "high"
                })
            if "목" in pain_areas or "어깨" in pain_areas:
                service_recommendations.append({
                    "service_name": "목/어깨 집중 케어",
                    "reason": "목/어깨 통증을 호소하셨습니다. 근막 이완과 스트레칭이 도움이 됩니다.",
                    "expected_benefit": "목/어깨 긴장 완화 및 유연성 향상",
                    "priority": "medium"
                })
    
    # 인바디 데이터가 있는 경우 추가 분석
    if latest_inbody:
        # 체지방률 기반 추천
        if latest_inbody.body_fat_percentage:
            if latest_inbody.body_fat_percentage > 30:
                care_recommendations.insert(0, {
                    "category": "체지방 관리",
                    "suggestion": "체지방률이 높은 편입니다. 유산소 운동과 식단 관리를 병행하시기를 권장합니다.",
                    "urgency": "immediate"
                })
            elif latest_inbody.body_fat_percentage < 15:
                care_recommendations.append({
                    "category": "영양 관리",
                    "suggestion": "체지방률이 낮은 편입니다. 균형 잡힌 영양 섭취가 필요합니다.",
                    "urgency": "soon"
                })
        
        # 근육량 기반 추천
        if latest_inbody.skeletal_muscle_mass:
            if latest_inbody.weight and latest_inbody.skeletal_muscle_mass / latest_inbody.weight < 0.3:
                service_recommendations.append({
                    "service_name": "근력 강화 프로그램",
                    "reason": "근육량이 부족한 편입니다. 저항 운동을 통한 근육 증진이 필요합니다.",
                    "expected_benefit": "근육량 증가 및 신체 기능 향상",
                    "priority": "medium"
                })
    
    # 종합 패키지 추천
    if latest_questionnaire and len(service_recommendations) >= 2:
        package_recommendations.insert(0, {
            "package_name": "AI 맞춤 종합 건강관리 패키지",
            "services_included": [rec["service_name"] for rec in service_recommendations[:3]],
            "discount_rate": 20,
            "recommended_price": 450000,
            "reason": "건강설문 분석 결과, 여러 영역의 관리가 필요합니다. 종합 패키지로 효율적인 관리를 받으세요."
        })
    
    # 영양제 추천 추가
    supplement_recommendations = []
    diet_recommendations = []
    health_analysis = {}
    
    if latest_questionnaire:
        # 기본 영양제 추천 (모든 고객에게 제공)
        supplement_recommendations.append({
            "name": "종합 멀티비타민",
            "reason": "일상 생활에서 부족하기 쉬운 필수 비타민과 미네랄을 보충합니다.",
            "dosage": "1일 1정",
            "price": 28000,
            "category": "기초 영양"
        })
        
        supplement_recommendations.append({
            "name": "오메가-3",
            "reason": "혈행 개선과 염증 감소에 도움을 주며, 뇌 건강과 심혈관 건강을 지원합니다.",
            "dosage": "1일 2정",
            "price": 32000,
            "category": "심혈관 건강"
        })
        # 피로도 분석
        fatigue_answer = next((a for a in answers if "피로" in a.question.question_text), None)
        if fatigue_answer and fatigue_answer.answer_number and fatigue_answer.answer_number >= 7:
            supplement_recommendations.append({
                "name": "종합 비타민 B",
                "reason": "높은 피로도를 호소하셨습니다. 비타민 B군은 에너지 대사를 도와 피로 개선에 효과적입니다.",
                "dosage": "1일 1정",
                "price": 35000,
                "category": "피로 개선"
            })
            
        # 수면 질 분석
        sleep_answer = next((a for a in answers if "수면" in a.question.question_text), None)
        if sleep_answer and sleep_answer.answer_value and ("나쁨" in sleep_answer.answer_value or "매우 나쁨" in sleep_answer.answer_value):
            supplement_recommendations.append({
                "name": "마그네슘 & L-테아닌",
                "reason": "수면의 질이 좋지 않다고 응답하셨습니다. 마그네슘과 L-테아닌은 신경 안정과 수면 개선에 도움을 줍니다.",
                "dosage": "취침 1시간 전 1정",
                "price": 42000,
                "category": "수면 개선"
            })
            
        # 소화기 건강 분석
        digestion_answer = next((a for a in answers if "소화" in a.question.question_text), None)
        if digestion_answer and digestion_answer.answer_value and ("불편" in digestion_answer.answer_value):
            supplement_recommendations.append({
                "name": "프로바이오틱스 복합제",
                "reason": "소화 불편을 겪고 계십니다. 유산균은 장 건강 개선과 소화 기능 향상에 도움이 됩니다.",
                "dosage": "1일 1포",
                "price": 48000,
                "category": "소화 건강"
            })
    
    # 인바디 데이터 기반 영양제 추천
    if latest_inbody:
        if latest_inbody.body_fat_percentage and latest_inbody.body_fat_percentage > 30:
            supplement_recommendations.append({
                "name": "가르시니아 & 녹차추출물",
                "reason": "체지방률 관리가 필요합니다. 지방 대사를 돕는 성분들이 체중 관리에 도움을 줄 수 있습니다.",
                "dosage": "1일 2정 (식전)",
                "price": 39000,
                "category": "체지방 관리"
            })
            
        if latest_inbody.skeletal_muscle_mass and latest_inbody.weight:
            muscle_ratio = latest_inbody.skeletal_muscle_mass / latest_inbody.weight
            if muscle_ratio < 0.3:
                supplement_recommendations.append({
                    "name": "BCAA & 크레아틴",
                    "reason": "근육량 증진이 필요합니다. BCAA와 크레아틴은 근육 성장과 회복에 도움을 줍니다.",
                    "dosage": "운동 전후 1스쿱",
                    "price": 55000,
                    "category": "근육 증진"
                })
    
    # 식단 추천
    if latest_questionnaire or latest_inbody:
        # 기본 건강 식단 추천 (모든 고객에게 제공)
        diet_recommendations.append({
            "meal_type": "아침",
            "menu": "통곡물 시리얼 + 우유 + 계절 과일",
            "calories": 400,
            "reason": "균형잡힌 아침 식사로 하루를 건강하게 시작하세요",
            "nutrients": {"protein": 15, "carbs": 65, "fat": 10}
        })
        
        diet_recommendations.append({
            "meal_type": "점심",
            "menu": "잡곡밥 + 생선구이 + 나물 반찬 3종",
            "calories": 550,
            "reason": "한식 위주의 균형잡힌 점심으로 포만감과 영양을 동시에",
            "nutrients": {"protein": 30, "carbs": 70, "fat": 15}
        })
        
        diet_recommendations.append({
            "meal_type": "저녁",
            "menu": "현미밥 + 된장찌개 + 두부조림 + 김치",
            "calories": 450,
            "reason": "소화가 편한 저녁 식사로 숙면에 도움",
            "nutrients": {"protein": 20, "carbs": 60, "fat": 12}
        })
        
        # 체중 관리가 필요한 경우 추가 권장사항
        if (latest_inbody and latest_inbody.body_fat_percentage and latest_inbody.body_fat_percentage > 25) or \
           ("weight_loss" in purposes):
            diet_recommendations.append({
                "meal_type": "아침",
                "menu": "그릭요거트 + 베리류 + 아몬드",
                "calories": 350,
                "reason": "고단백 저칼로리 아침으로 포만감 유지와 대사 활성화",
                "nutrients": {"protein": 20, "carbs": 35, "fat": 12}
            })
            diet_recommendations.append({
                "meal_type": "점심",
                "menu": "현미밥 + 닭가슴살 샐러드 + 야채 반찬",
                "calories": 450,
                "reason": "균형잡힌 영양소와 적절한 칼로리로 체중 관리",
                "nutrients": {"protein": 35, "carbs": 45, "fat": 15}
            })
            diet_recommendations.append({
                "meal_type": "저녁",
                "menu": "두부 스테이크 + 구운 야채 + 미역국",
                "calories": 380,
                "reason": "저녁은 가볍게, 단백질 위주로 구성",
                "nutrients": {"protein": 25, "carbs": 30, "fat": 18}
            })
            
        # 근육 증진이 필요한 경우
        elif "muscle_gain" in purposes:
            diet_recommendations.append({
                "meal_type": "아침",
                "menu": "스크램블 에그 3개 + 통밀빵 + 아보카도",
                "calories": 520,
                "reason": "근육 성장을 위한 고단백 아침 식사",
                "nutrients": {"protein": 30, "carbs": 45, "fat": 22}
            })
            diet_recommendations.append({
                "meal_type": "운동 후",
                "menu": "프로틴 쉐이크 + 바나나 + 견과류",
                "calories": 400,
                "reason": "운동 후 30분 이내 섭취로 근육 회복 촉진",
                "nutrients": {"protein": 35, "carbs": 40, "fat": 10}
            })
    
    # 건강 분석 요약
    if latest_questionnaire:
        # 세포 나이 계산 (예시 로직)
        cellular_age = customer.birth_year + 20 if customer.birth_year else 40
        if latest_inbody and latest_inbody.body_fat_percentage:
            if latest_inbody.body_fat_percentage > 30:
                cellular_age += 5
            elif latest_inbody.body_fat_percentage < 20:
                cellular_age -= 3
        
        # 건강 점수 계산
        overall_score = 75.0  # 기본 점수
        category_scores = {
            "body_composition": 70.0,
            "metabolic_health": 75.0,
            "stress_management": 65.0,
            "vitality": 80.0,
            "nutrition": 70.0
        }
        
        # 인바디 데이터 기반 점수 조정
        if latest_inbody:
            if latest_inbody.body_fat_percentage:
                if latest_inbody.body_fat_percentage < 25:
                    category_scores["body_composition"] = 85.0
                elif latest_inbody.body_fat_percentage > 30:
                    category_scores["body_composition"] = 60.0
            
            if latest_inbody.visceral_fat_level:
                if latest_inbody.visceral_fat_level < 10:
                    category_scores["metabolic_health"] = 85.0
                elif latest_inbody.visceral_fat_level > 15:
                    category_scores["metabolic_health"] = 55.0
        
        # 문진 답변 기반 점수 조정
        if stress_answer and stress_answer.answer_number:
            if stress_answer.answer_number >= 7:
                category_scores["stress_management"] = 45.0
            elif stress_answer.answer_number <= 3:
                category_scores["stress_management"] = 85.0
        
        # 전체 점수 재계산
        overall_score = sum(category_scores.values()) / len(category_scores)
        
        health_analysis = {
            "cellular_age": cellular_age,
            "age_gap": cellular_age - (2025 - customer.birth_year) if customer.birth_year else 0,
            "overall_score": overall_score,
            "category_scores": category_scores,
            "overall_status": "종합 건강 상태",
            "main_concerns": [],
            "strengths": [],
            "improvement_areas": []
        }
        
        # 주요 우려사항 분석
        if stress_answer and stress_answer.answer_number and stress_answer.answer_number >= 7:
            health_analysis["main_concerns"].append("높은 스트레스 수준")
        if fatigue_answer and fatigue_answer.answer_number and fatigue_answer.answer_number >= 7:
            health_analysis["main_concerns"].append("만성 피로")
        if pain_answer and pain_answer.answer_value:
            health_analysis["main_concerns"].append(f"근골격계 통증 ({pain_answer.answer_value})")
            
        # 강점 분석
        exercise_answer = next((a for a in answers if "운동" in a.question.question_text), None)
        if exercise_answer and exercise_answer.answer_value and "규칙적" in exercise_answer.answer_value:
            health_analysis["strengths"].append("규칙적인 운동 습관")
            
        # 개선 필요 영역
        if latest_inbody and latest_inbody.body_fat_percentage and latest_inbody.body_fat_percentage > 30:
            health_analysis["improvement_areas"].append("체지방률 관리")
        if latest_inbody and latest_inbody.visceral_fat_level and latest_inbody.visceral_fat_level > 10:
            health_analysis["improvement_areas"].append("내장지방 감소")
    
    # 결과 반환
    return {
        "has_health_data": True,
        "service_recommendations": service_recommendations[:5],  # 최대 5개
        "package_recommendations": package_recommendations[:3],  # 최대 3개
        "care_recommendations": care_recommendations[:5],  # 최대 5개
        "supplement_recommendations": supplement_recommendations[:4],  # 최대 4개
        "diet_recommendations": diet_recommendations[:3],  # 최대 3개
        "health_analysis": health_analysis
    }

@router.get("/{customer_id}/packages")
async def get_customer_packages(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """고객의 패키지 구매 내역 조회"""
    try:
        # 패키지 구매 내역 조회
        packages_query = text("""
            SELECT 
                pp.purchase_id,
                pp.package_id,
                p.package_name,
                pp.purchase_date,
                pp.expiry_date,
                pp.total_sessions,
                pp.used_sessions,
                pp.remaining_sessions,
                p.price,
                CASE 
                    WHEN pp.expiry_date < CURRENT_DATE THEN 'expired'
                    WHEN pp.remaining_sessions = 0 THEN 'completed'
                    ELSE 'active'
                END as status
            FROM package_purchases pp
            JOIN packages p ON pp.package_id = p.package_id
            WHERE pp.customer_id = :customer_id
            ORDER BY pp.purchase_date DESC
        """)
        
        packages = db.execute(packages_query, {"customer_id": customer_id}).fetchall()
        
        result = []
        for pkg in packages:
            result.append({
                "purchase_id": pkg.purchase_id,
                "package_id": pkg.package_id,
                "package_name": pkg.package_name,
                "purchase_date": pkg.purchase_date.isoformat() if pkg.purchase_date else None,
                "expiry_date": pkg.expiry_date.isoformat() if pkg.expiry_date else None,
                "total_sessions": pkg.total_sessions,
                "used_sessions": pkg.used_sessions,
                "remaining_sessions": pkg.remaining_sessions,
                "price": float(pkg.price) if pkg.price else 0,
                "status": pkg.status
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting customer packages: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"패키지 조회 중 오류가 발생했습니다: {str(e)}"
        )
