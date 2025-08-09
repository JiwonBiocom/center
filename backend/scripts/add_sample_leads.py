import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from models.lead import MarketingLead
from datetime import date, timedelta
import random

def add_sample_leads():
    session = SessionLocal()
    try:
        # 채널별 리드 생성
        channels = ['유튜브', '당근', '메타', '검색', '지인소개', '인스타그램']
        names = [
            '김민지', '이준호', '박서연', '최동훈', '정예린', 
            '강태우', '신지원', '오하늘', '윤재민', '임수빈',
            '한지우', '조은서', '배성민', '문예준', '권나연',
            '홍서준', '서민재', '안유진', '김도현', '이서윤'
        ]
        
        leads = []
        today = date.today()
        
        for i, name in enumerate(names):
            # 리드 날짜 (최근 30일 내)
            lead_date = today - timedelta(days=random.randint(0, 30))
            channel = random.choice(channels)
            
            # 상태에 따른 날짜 설정
            status_choice = random.random()
            
            lead = MarketingLead(
                name=name,
                phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                lead_date=lead_date,
                channel=channel
            )
            
            # 90% DB 입력
            if status_choice > 0.1:
                lead.db_entry_date = lead_date + timedelta(days=random.randint(0, 2))
                lead.status = 'db_entered'
                
                # 70% 전화상담
                if status_choice > 0.3:
                    lead.phone_consult_date = lead.db_entry_date + timedelta(days=random.randint(1, 3))
                    lead.status = 'phone_consulted'
                    
                    # 50% 방문상담
                    if status_choice > 0.5:
                        lead.visit_consult_date = lead.phone_consult_date + timedelta(days=random.randint(1, 5))
                        lead.status = 'visit_consulted'
                        
                        # 15% 등록완료
                        if status_choice > 0.85:
                            lead.registration_date = lead.visit_consult_date + timedelta(days=random.randint(0, 2))
                            lead.status = 'converted'
            
            leads.append(lead)
        
        # 일부 추가 리드 (유튜브 집중)
        for i in range(10):
            lead = MarketingLead(
                name=f"유튜브고객{i+1}",
                phone=f"010-5555-{1000+i:04d}",
                lead_date=today - timedelta(days=random.randint(0, 14)),
                channel='유튜브',
                status='new'
            )
            leads.append(lead)
        
        # 모든 리드 추가
        for lead in leads:
            session.add(lead)
        
        session.commit()
        print(f"Added {len(leads)} sample leads")
    finally:
        session.close()

if __name__ == "__main__":
    add_sample_leads()