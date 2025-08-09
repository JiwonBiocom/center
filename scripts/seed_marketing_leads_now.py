#!/usr/bin/env python3
"""
유입고객 데이터를 즉시 시드하는 스크립트
lead_date 필수 필드 처리
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from backend.core.database import engine
from backend.models.customer_extended import MarketingLead
from sqlalchemy.orm import Session
from sqlalchemy import text
import re

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

def parse_age(age_value):
    """나이 파싱 - '28세' -> 28"""
    if pd.isna(age_value):
        return None
    
    age_str = str(age_value)
    numbers = re.findall(r'\d+', age_str)
    if numbers:
        age = int(numbers[0])
        if 0 < age < 120:
            return age
    return None

def parse_date(date_value):
    """엑셀 날짜 값을 파싱"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()
    
    if isinstance(date_value, str):
        try:
            return pd.to_datetime(date_value).date()
        except:
            return None
    
    return None

def parse_revenue(value):
    """매출 금액 파싱"""
    if pd.isna(value):
        return 0
    
    if isinstance(value, (int, float)):
        revenue = int(value)
        if revenue > 2147483647:
            return 2147483647
        return revenue
    
    value_str = str(value).replace(',', '').replace('원', '').replace(' ', '')
    try:
        numbers = re.findall(r'\d+', value_str)
        if numbers:
            revenue = int(numbers[0])
            if revenue > 2147483647:
                return 2147483647
            return revenue
    except:
        pass
    
    return 0

def main():
    print("🚀 유입고객 데이터 시드 시작...")
    
    # Excel 파일 읽기
    excel_path = "backend/seed/marketing_leads.xlsx"
    df = pd.read_excel(excel_path)
    print(f"📊 총 {len(df)}개 행 발견")
    
    with Session(engine) as session:
        # 기존 데이터 삭제
        print("\n🧹 기존 데이터 정리 중...")
        session.execute(text("DELETE FROM marketing_leads"))
        session.commit()
        
        success_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # 필수 필드 확인
                name = row.get('이름')
                if pd.isna(name) or not name:
                    continue
                
                # lead_date 결정 (필수 필드)
                lead_date = parse_date(row.get('DB입력일'))
                if not lead_date:
                    # DB입력일이 없으면 다른 날짜 필드 사용
                    lead_date = parse_date(row.get('전화상담일'))
                    if not lead_date:
                        lead_date = parse_date(row.get('방문상담일'))
                        if not lead_date:
                            lead_date = parse_date(row.get('등록일'))
                            if not lead_date:
                                # 모든 날짜가 없으면 오늘 날짜 사용
                                lead_date = datetime.now().date()
                
                # 새 리드 생성
                lead = MarketingLead(
                    name=str(name).strip(),
                    phone=clean_phone_number(row.get('연락처')),
                    lead_date=lead_date,  # 필수 필드
                    age=parse_age(row.get('나이')),
                    region=row.get('거주지역') if pd.notna(row.get('거주지역')) else None,
                    lead_channel=row.get('유입경로') if pd.notna(row.get('유입경로')) else None,
                    carrot_id=row.get('당근아이디') if pd.notna(row.get('당근아이디')) else None,
                    ad_watched=row.get('시청 광고') if pd.notna(row.get('시청 광고')) else None,
                    price_informed=row.get('가격안내') == 'O' if pd.notna(row.get('가격안내')) else False,
                    ab_test_group=row.get('A/B 테스트') if pd.notna(row.get('A/B 테스트')) else None,
                    db_entry_date=parse_date(row.get('DB입력일')),
                    phone_consult_date=parse_date(row.get('전화상담일')),
                    visit_consult_date=parse_date(row.get('방문상담일')),
                    registration_date=parse_date(row.get('등록일')),
                    purchased_product=row.get('구매상품') if pd.notna(row.get('구매상품')) else None,
                    no_registration_reason=row.get('미등록사유') if pd.notna(row.get('미등록사유')) else None,
                    notes=row.get('비고') if pd.notna(row.get('비고')) else None,
                    revenue=parse_revenue(row.get('매출')),
                    status='new'
                )
                
                session.add(lead)
                success_count += 1
                
                # 진행 상황 표시
                if success_count % 20 == 0:
                    print(f"  처리 중... {success_count}개 완료")
                    session.commit()
                
            except Exception as e:
                error_count += 1
                print(f"❌ 행 {idx+2} 오류: {str(e)}")
                session.rollback()
                continue
        
        # 최종 커밋
        session.commit()
        
        # 결과 확인
        total_count = session.execute(text("SELECT COUNT(*) FROM marketing_leads")).scalar()
        
        print(f"\n✅ 유입고객 데이터 시드 완료!")
        print(f"   - 성공: {success_count}개")
        print(f"   - 실패: {error_count}개")
        print(f"   - 전체 레코드: {total_count}개")
        
        # 샘플 데이터 확인
        samples = session.execute(text("""
            SELECT name, phone, age, revenue, lead_date 
            FROM marketing_leads 
            ORDER BY lead_id DESC 
            LIMIT 5
        """)).fetchall()
        
        if samples:
            print(f"\n📋 최근 추가된 데이터 샘플:")
            for sample in samples:
                print(f"   - {sample[0]}, {sample[1]}, {sample[2]}세, {sample[3]:,}원, {sample[4]}")

if __name__ == "__main__":
    main()