#!/usr/bin/env python3
"""실제 유입고객 데이터 마이그레이션 스크립트"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from core.database import engine
from models.customer_extended import MarketingLead
from models.customer import Customer
from datetime import datetime, date
import re

def clean_phone_number(phone):
    """전화번호 정리"""
    if pd.isna(phone) or not phone:
        return None
    
    phone = str(phone).strip()
    # 숫자만 추출
    phone = re.sub(r'[^\d]', '', phone)
    
    # 10자리 또는 11자리만 유효
    if len(phone) in [10, 11]:
        # 010-xxxx-xxxx 형식으로 변환
        if len(phone) == 10:
            return f"010-{phone[3:7]}-{phone[7:]}"
        else:
            return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    
    return None

def parse_date(date_str):
    """날짜 문자열 파싱"""
    if pd.isna(date_str) or not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # 다양한 날짜 형식 처리
    date_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%Y.%m.%d',
        '%Y/%m/%d',
        '%Y%m%d'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    
    return None

def parse_revenue(revenue_str):
    """매출 데이터 파싱"""
    if pd.isna(revenue_str) or not revenue_str:
        return None
    
    try:
        # 쉼표 제거하고 숫자로 변환
        revenue = str(revenue_str).replace(',', '').replace('원', '').strip()
        return float(revenue)
    except:
        return None

def parse_boolean(val):
    """불린 값 파싱"""
    if pd.isna(val) or not val:
        return False
    
    val = str(val).strip().lower()
    return val in ['y', 'yes', 'o', 'true', '1', '예', '네']

def parse_age(age_str):
    """나이 문자열을 숫자로 변환"""
    if pd.isna(age_str) or not age_str:
        return None
    
    try:
        # 문자열에서 숫자만 추출 (예: "28세" -> 28)
        age_str = str(age_str)
        import re
        numbers = re.findall(r'\d+', age_str)
        if numbers:
            return int(numbers[0])
        return None
    except:
        return None

def determine_status(row):
    """리드 상태 결정"""
    if pd.notna(row.get('등록일')):
        return 'converted'
    elif pd.notna(row.get('방문상담일')):
        return 'visit_consulted'
    elif pd.notna(row.get('전화상담일')):
        return 'phone_consulted'
    elif pd.notna(row.get('DB입력일')):
        return 'db_entered'
    else:
        return 'new'

def delete_sample_leads(session):
    """샘플/테스트 리드 삭제"""
    print("\n=== 기존 샘플 데이터 삭제 ===")
    
    # 테스트 패턴이 있는 리드 삭제
    test_patterns = ['테스트', 'test', 'Test', 'TEST', '샘플', 'sample']
    deleted_count = 0
    
    for pattern in test_patterns:
        result = session.execute(
            delete(MarketingLead)
            .where(
                (MarketingLead.name.like(f'%{pattern}%')) |
                (MarketingLead.notes.like(f'%{pattern}%'))
            )
        )
        deleted_count += result.rowcount
    
    # 연속된 번호 패턴의 전화번호 삭제
    sequential_patterns = ['%1234%', '%5678%', '%0000%', '%1111%', '%2222%', '%3333%']
    for pattern in sequential_patterns:
        result = session.execute(
            delete(MarketingLead)
            .where(MarketingLead.phone.like(pattern))
        )
        deleted_count += result.rowcount
    
    session.commit()
    print(f"삭제된 샘플 리드: {deleted_count}개")
    
    return deleted_count

def migrate_leads():
    """실제 리드 데이터 마이그레이션"""
    
    csv_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/유입고객_DB리스트.csv"
    
    # CSV 파일 읽기
    print("=== CSV 파일 읽기 ===")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"전체 행 수: {len(df)}개")
    
    with Session(engine) as session:
        # 1. 기존 샘플 데이터 삭제
        delete_sample_leads(session)
        
        # 2. 모든 기존 리드 삭제 (옵션)
        print("\n=== 기존 리드 데이터 전체 삭제 ===")
        result = session.execute(delete(MarketingLead))
        print(f"삭제된 기존 리드: {result.rowcount}개")
        session.commit()
        
        # 3. 새 리드 데이터 마이그레이션
        print("\n=== 새 리드 데이터 마이그레이션 ===")
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 필수 필드 검증
                name = row.get('이름')
                if pd.isna(name) or not name:
                    error_count += 1
                    errors.append(f"행 {index + 2}: 이름이 없습니다")
                    continue
                
                # 전화번호 정리
                phone = clean_phone_number(row.get('연락처'))
                
                # 리드 데이터 생성
                lead_data = {
                    'name': str(name).strip(),
                    'phone': phone,
                    'age': parse_age(row.get('나이')),
                    'region': str(row.get('거주지역')).strip() if pd.notna(row.get('거주지역')) else None,
                    'lead_channel': str(row.get('유입경로')).strip() if pd.notna(row.get('유입경로')) else None,
                    'carrot_id': str(row.get('당근아이디')).strip() if pd.notna(row.get('당근아이디')) else None,
                    'ad_watched': str(row.get('시청 광고')).strip() if pd.notna(row.get('시청 광고')) else None,
                    'price_informed': parse_boolean(row.get('가격안내')),
                    'ab_test_group': str(row.get('A/B 테스트')).strip() if pd.notna(row.get('A/B 테스트')) else None,
                    'db_entry_date': parse_date(row.get('DB입력일')),
                    'phone_consult_date': parse_date(row.get('전화상담일')),
                    'visit_consult_date': parse_date(row.get('방문상담일')),
                    'registration_date': parse_date(row.get('등록일')),
                    'purchased_product': str(row.get('구매상품')).strip() if pd.notna(row.get('구매상품')) else None,
                    'no_registration_reason': str(row.get('미등록사유')).strip() if pd.notna(row.get('미등록사유')) else None,
                    'notes': str(row.get('비고')).strip() if pd.notna(row.get('비고')) else None,
                    'revenue': parse_revenue(row.get('매출')),
                    'status': determine_status(row)
                }
                
                # 추가 필드 처리
                # DB작성 채널을 notes에 추가
                if pd.notna(row.get('DB작성 채널')):
                    db_channel = f"DB작성채널: {row.get('DB작성 채널')}"
                    if lead_data['notes']:
                        lead_data['notes'] = f"{lead_data['notes']}\n{db_channel}"
                    else:
                        lead_data['notes'] = db_channel
                
                # lead_date 설정 (DB입력일을 기본으로)
                if lead_data['db_entry_date']:
                    lead_data['lead_date'] = lead_data['db_entry_date']
                else:
                    lead_data['lead_date'] = date.today()
                
                # 리드 생성
                lead = MarketingLead(**lead_data)
                session.add(lead)
                success_count += 1
                
                # 진행 상황 출력
                if (index + 1) % 10 == 0:
                    print(f"  진행중... {index + 1}/{len(df)}")
                    
            except Exception as e:
                error_count += 1
                errors.append(f"행 {index + 2}: {str(e)}")
                if error_count <= 10:  # 처음 10개 에러만 상세 출력
                    print(f"  에러 - 행 {index + 2}: {str(e)}")
        
        # 커밋
        session.commit()
        print(f"\n마이그레이션 완료!")
        print(f"  - 성공: {success_count}개")
        print(f"  - 실패: {error_count}개")
        
        if errors and error_count > 10:
            print(f"\n[추가 에러 {error_count - 10}개 생략...]")
        
        # 4. 결과 확인
        print("\n=== 마이그레이션 결과 확인 ===")
        total_count = session.query(MarketingLead).count()
        print(f"총 리드 수: {total_count}개")
        
        # 상태별 통계
        status_stats = session.query(
            MarketingLead.status,
            session.query(MarketingLead).filter(MarketingLead.status == MarketingLead.status).count()
        ).group_by(MarketingLead.status).all()
        
        print("\n[상태별 통계]")
        for status, count in status_stats:
            print(f"  - {status}: {count}개")

def main():
    """메인 함수"""
    print("유입고객 데이터 마이그레이션을 시작합니다.")
    print("주의: 기존 리드 데이터가 모두 삭제되고 새로 입력됩니다!")
    
    # 자동 실행을 위해 확인 과정 생략
    print("\n자동 실행 모드로 진행합니다...")
    
    migrate_leads()

if __name__ == "__main__":
    main()