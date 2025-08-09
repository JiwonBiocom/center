"""
유입고객 데이터 마이그레이션 스크립트
- notes 필드에서 DB작성 채널 추출
- 고객 서비스 이용 정보에서 마지막 이용일 계산
- 재등록 대상 자동 선별
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_ as db_or
import re

from core.database import SessionLocal
from models.customer_extended import MarketingLead
from models.service import ServiceUsage
from models.customer import Customer

def extract_db_channel_from_notes():
    """notes 필드에서 DB작성 채널 추출"""
    db = SessionLocal()
    
    try:
        # DB작성채널이 있는 notes를 가진 리드들
        leads = db.query(MarketingLead).filter(
            and_(
                MarketingLead.notes.like('%DB작성채널:%'),
                MarketingLead.db_channel.is_(None)
            )
        ).all()
        
        print(f"DB작성 채널 추출 대상: {len(leads)}개")
        
        for lead in leads:
            # notes에서 DB작성채널 추출
            match = re.search(r'DB작성채널:\s*([^\n]+)', lead.notes)
            if match:
                db_channel = match.group(1).strip()
                lead.db_channel = db_channel
                print(f"- {lead.name}: {db_channel}")
        
        db.commit()
        print(f"✅ DB작성 채널 추출 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()


def update_last_service_dates():
    """고객의 마지막 서비스 이용일 업데이트"""
    db = SessionLocal()
    
    try:
        # 고객으로 전환된 리드들
        converted_leads = db.query(MarketingLead).filter(
            MarketingLead.converted_customer_id.isnot(None)
        ).all()
        
        print(f"\n마지막 서비스 이용일 업데이트 대상: {len(converted_leads)}개")
        
        updated_count = 0
        for lead in converted_leads:
            # 해당 고객의 마지막 서비스 이용일 조회
            last_service = db.query(ServiceUsage).filter(
                ServiceUsage.customer_id == lead.converted_customer_id
            ).order_by(ServiceUsage.usage_date.desc()).first()
            
            if last_service:
                lead.last_service_date = last_service.usage_date
                updated_count += 1
        
        db.commit()
        print(f"✅ {updated_count}개의 마지막 서비스 이용일 업데이트 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()


def identify_reregistration_targets():
    """재등록 대상 자동 선별"""
    db = SessionLocal()
    
    try:
        # 기준일 (3개월 전)
        cutoff_date = date.today() - timedelta(days=90)
        
        # 1. 마지막 이용일이 3개월 이상 된 고객
        old_customers = db.query(MarketingLead).filter(
            and_(
                MarketingLead.last_service_date.isnot(None),
                MarketingLead.last_service_date <= cutoff_date
            )
        ).all()
        
        print(f"\n재등록 대상 선별:")
        print(f"- 3개월 이상 미이용 고객: {len(old_customers)}명")
        
        for lead in old_customers:
            lead.is_reregistration_target = True
        
        # 2. 등록하지 않은 상담 고객 (방문상담까지 했지만 미등록)
        no_registration = db.query(MarketingLead).filter(
            and_(
                MarketingLead.visit_consult_date.isnot(None),
                MarketingLead.registration_date.is_(None),
                MarketingLead.visit_consult_date <= date.today() - timedelta(days=30)  # 방문상담 후 30일 경과
            )
        ).all()
        
        print(f"- 방문상담 후 미등록 고객: {len(no_registration)}명")
        
        for lead in no_registration:
            lead.is_reregistration_target = True
        
        # 3. 특정 미등록 사유를 가진 고객
        target_reasons = ['가격', '시간', '거리']
        reason_customers = db.query(MarketingLead).filter(
            and_(
                MarketingLead.no_registration_reason.isnot(None),
                db_or(*[MarketingLead.no_registration_reason.like(f'%{reason}%') for reason in target_reasons])
            )
        ).all()
        
        print(f"- 특정 미등록 사유 고객: {len(reason_customers)}명")
        
        for lead in reason_customers:
            lead.is_reregistration_target = True
        
        db.commit()
        
        # 전체 재등록 대상 수 확인
        total_targets = db.query(MarketingLead).filter(
            MarketingLead.is_reregistration_target == True
        ).count()
        
        print(f"\n✅ 총 재등록 대상: {total_targets}명")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()


def update_lead_status():
    """리드 상태 재계산"""
    db = SessionLocal()
    
    try:
        leads = db.query(MarketingLead).all()
        
        print(f"\n리드 상태 업데이트 대상: {len(leads)}개")
        
        status_count = {
            'new': 0,
            'db_entered': 0,
            'phone_consulted': 0,
            'visit_consulted': 0,
            'converted': 0
        }
        
        for lead in leads:
            # 상태 재계산
            if lead.registration_date:
                lead.status = 'converted'
            elif lead.visit_consult_date:
                lead.status = 'visit_consulted'
            elif lead.phone_consult_date:
                lead.status = 'phone_consulted'
            elif lead.db_entry_date:
                lead.status = 'db_entered'
            else:
                lead.status = 'new'
            
            status_count[lead.status] += 1
        
        db.commit()
        
        print("✅ 리드 상태 업데이트 완료:")
        for status, count in status_count.items():
            print(f"  - {status}: {count}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()


def main():
    print("=" * 60)
    print("유입고객 데이터 마이그레이션")
    print("=" * 60)
    print(f"실행 시간: {datetime.now()}")
    
    # 1. notes에서 DB작성 채널 추출
    extract_db_channel_from_notes()
    
    # 2. 마지막 서비스 이용일 업데이트
    update_last_service_dates()
    
    # 3. 재등록 대상 선별
    identify_reregistration_targets()
    
    # 4. 리드 상태 재계산
    update_lead_status()
    
    print("\n✅ 마이그레이션 완료!")


if __name__ == "__main__":
    main()