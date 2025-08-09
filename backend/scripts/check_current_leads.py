#!/usr/bin/env python3
"""현재 데이터베이스의 리드 데이터 확인"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from core.database import engine
from models.customer_extended import MarketingLead
from datetime import datetime

def check_current_leads():
    """현재 데이터베이스의 리드 데이터 상태 확인"""
    
    with Session(engine) as session:
        # 전체 리드 수
        total_count = session.execute(select(func.count(MarketingLead.lead_id))).scalar()
        print(f"\n=== 현재 리드 데이터 현황 ===")
        print(f"전체 리드 수: {total_count}개")
        
        if total_count == 0:
            print("\n현재 데이터베이스에 리드 데이터가 없습니다.")
            return
        
        # 상태별 통계
        print("\n[상태별 통계]")
        status_stats = session.execute(
            select(
                MarketingLead.status,
                func.count(MarketingLead.lead_id)
            )
            .group_by(MarketingLead.status)
            .order_by(func.count(MarketingLead.lead_id).desc())
        ).all()
        
        for status, count in status_stats:
            print(f"  - {status or '미설정'}: {count}개")
        
        # 채널별 통계
        print("\n[채널별 통계]")
        channel_stats = session.execute(
            select(
                MarketingLead.lead_channel,
                func.count(MarketingLead.lead_id)
            )
            .group_by(MarketingLead.lead_channel)
            .order_by(func.count(MarketingLead.lead_id).desc())
        ).all()
        
        for channel, count in channel_stats:
            print(f"  - {channel or '미설정'}: {count}개")
        
        # 샘플 데이터 여부 확인 (동일한 패턴의 이름이나 전화번호가 있는지)
        print("\n[샘플 데이터 여부 확인]")
        
        # 테스트 패턴이 있는 리드 확인
        test_patterns = ['테스트', 'test', 'Test', 'TEST', '샘플', 'sample']
        test_leads = []
        
        for pattern in test_patterns:
            leads = session.execute(
                select(MarketingLead)
                .where(
                    (MarketingLead.name.like(f'%{pattern}%')) |
                    (MarketingLead.notes.like(f'%{pattern}%'))
                )
            ).scalars().all()
            test_leads.extend(leads)
        
        # 연속된 번호 패턴의 전화번호 확인
        sequential_phone_leads = session.execute(
            select(MarketingLead)
            .where(
                (MarketingLead.phone.like('%1234%')) |
                (MarketingLead.phone.like('%5678%')) |
                (MarketingLead.phone.like('%0000%')) |
                (MarketingLead.phone.like('%1111%'))
            )
        ).scalars().all()
        
        test_leads.extend(sequential_phone_leads)
        
        # 중복 제거
        unique_test_leads = list({lead.lead_id: lead for lead in test_leads}.values())
        
        if unique_test_leads:
            print(f"  - 샘플/테스트로 추정되는 리드: {len(unique_test_leads)}개")
            print("\n  [샘플 데이터 예시]")
            for i, lead in enumerate(unique_test_leads[:5]):  # 최대 5개만 표시
                print(f"    {i+1}. {lead.name} | {lead.phone} | {lead.lead_channel} | {lead.notes[:30] if lead.notes else ''}")
        else:
            print("  - 샘플/테스트 데이터가 발견되지 않았습니다.")
        
        # 최근 데이터 확인
        print("\n[최근 등록된 리드 (최대 5개)]")
        recent_leads = session.execute(
            select(MarketingLead)
            .order_by(MarketingLead.created_at.desc())
            .limit(5)
        ).scalars().all()
        
        for i, lead in enumerate(recent_leads):
            print(f"  {i+1}. {lead.name} | {lead.phone} | {lead.lead_channel} | {lead.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 날짜 범위 확인
        print("\n[날짜 범위]")
        date_range = session.execute(
            select(
                func.min(MarketingLead.created_at),
                func.max(MarketingLead.created_at)
            )
        ).first()
        
        if date_range[0] and date_range[1]:
            print(f"  - 첫 리드 등록일: {date_range[0].strftime('%Y-%m-%d')}")
            print(f"  - 마지막 리드 등록일: {date_range[1].strftime('%Y-%m-%d')}")
        
        # 전환율 통계
        print("\n[전환 통계]")
        converted_count = session.execute(
            select(func.count(MarketingLead.lead_id))
            .where(MarketingLead.converted_customer_id.is_not(None))
        ).scalar()
        
        print(f"  - 고객으로 전환된 리드: {converted_count}개 ({converted_count/total_count*100:.1f}%)")
        
        # 매출 통계
        revenue_stats = session.execute(
            select(
                func.count(MarketingLead.lead_id),
                func.sum(MarketingLead.revenue)
            )
            .where(MarketingLead.revenue.is_not(None))
        ).first()
        
        if revenue_stats[0] > 0:
            print(f"  - 매출이 기록된 리드: {revenue_stats[0]}개")
            print(f"  - 총 매출액: {revenue_stats[1]:,.0f}원")

if __name__ == "__main__":
    check_current_leads()