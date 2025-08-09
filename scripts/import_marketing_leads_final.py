#!/usr/bin/env python3
"""
유입고객(marketing_leads) 데이터를 프로덕션 DB에 시드하는 스크립트 - 최종 수정 버전
데이터 타입 문제 해결
"""

import sys
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from datetime import datetime
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
    # 숫자만 추출
    numbers = re.findall(r'\d+', age_str)
    if numbers:
        age = int(numbers[0])
        # 합리적인 나이 범위 체크
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

def parse_boolean(value):
    """불린 값 파싱"""
    if pd.isna(value):
        return False
    
    value_str = str(value).strip().lower()
    return value_str in ['yes', 'y', 'true', '1', '예', 'o']

def parse_revenue(value):
    """매출 금액 파싱 - integer 범위 체크"""
    if pd.isna(value):
        return 0
    
    if isinstance(value, (int, float)):
        # PostgreSQL integer 범위: -2147483648 to 2147483647
        revenue = int(value)
        if revenue > 2147483647:
            return 2147483647  # 최대값으로 제한
        return revenue
    
    # 문자열에서 숫자만 추출
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
    print("🚀 유입고객 데이터 시드 시작 (최종 버전)...")
    
    # 환경 변수에서 DB 정보 가져오기
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # Excel 파일 경로
    excel_path = "backend/seed/marketing_leads.xlsx"
    if not os.path.exists(excel_path):
        print(f"⚠️  {excel_path} 파일이 없습니다. 건너뜁니다.")
        sys.exit(0)
    
    # Excel 파일 읽기
    print(f"📖 {excel_path} 읽는 중...")
    df = pd.read_excel(excel_path)
    print(f"📊 총 {len(df)}개 행 발견")
    
    # DB 연결
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        sslmode='require'
    )
    cur = conn.cursor()
    
    # 테이블 구조 확인
    print("\n📋 테이블 구조 확인 중...")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'marketing_leads'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    print(f"주요 컬럼:")
    for col_name, col_type in columns[:10]:
        print(f"  - {col_name}: {col_type}")
    
    # 기존 테스트 데이터 삭제
    print("\n🧹 기존 테스트 데이터 정리 중...")
    test_patterns = ['테스트', 'test', 'Test', 'TEST', '샘플', 'sample']
    for pattern in test_patterns:
        cur.execute("""
            DELETE FROM marketing_leads 
            WHERE name LIKE %s OR notes LIKE %s
        """, (f'%{pattern}%', f'%{pattern}%'))
    
    conn.commit()
    
    # 데이터 삽입/업데이트
    success_count = 0
    error_count = 0
    
    for idx, row in df.iterrows():
        try:
            # 필수 필드 확인
            name = row.get('이름', row.get('lead_name', row.get('name')))
            if pd.isna(name) or not name:
                print(f"⚠️  행 {idx+2}: 이름이 없습니다. 건너뜁니다.")
                continue
            
            # 데이터 준비
            phone = clean_phone_number(row.get('연락처', row.get('phone', row.get('lead_phone'))))
            
            # 기존 레코드 확인
            cur.execute("""
                SELECT lead_id FROM marketing_leads 
                WHERE name = %s AND phone = %s
            """, (name, phone))
            
            existing = cur.fetchone()
            
            # 나이 파싱
            age = parse_age(row.get('나이', row.get('age')))
            
            # 매출 파싱  
            revenue = parse_revenue(row.get('매출', row.get('revenue')))
            
            lead_data = {
                'name': str(name).strip(),
                'phone': phone,
                'age': age,  # 정수로 변환됨
                'region': row.get('거주지역', row.get('region')),
                'lead_channel': row.get('유입경로', row.get('lead_source', row.get('lead_channel'))),
                'carrot_id': row.get('당근아이디', row.get('carrot_id')),
                'ad_watched': row.get('시청 광고', row.get('ad_content', row.get('ad_watched'))),
                'price_informed': parse_boolean(row.get('가격안내', row.get('price_informed'))),
                'ab_test_group': row.get('A/B 테스트', row.get('ab_test_group')),
                'db_entry_date': parse_date(row.get('DB입력일', row.get('lead_date', row.get('db_entry_date')))),
                'phone_consult_date': parse_date(row.get('전화상담일', row.get('phone_consultation_date'))),
                'visit_consult_date': parse_date(row.get('방문상담일', row.get('visit_consultation_date'))),
                'registration_date': parse_date(row.get('등록일', row.get('registration_date'))),
                'purchased_product': row.get('구매상품', row.get('purchased_product')),
                'no_registration_reason': row.get('미등록사유', row.get('no_registration_reason')),
                'notes': row.get('비고', row.get('notes')),
                'revenue': revenue,  # 정수 범위 체크됨
                'status': row.get('상태', row.get('status', 'new'))
            }
            
            # None 값 제거
            lead_data = {k: v for k, v in lead_data.items() if v is not None}
            
            if existing:
                # UPDATE
                lead_id = existing[0]
                set_clause = ', '.join([f"{k} = %s" for k in lead_data.keys()])
                values = list(lead_data.values()) + [lead_id]
                
                cur.execute(f"""
                    UPDATE marketing_leads 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE lead_id = %s
                """, values)
            else:
                # INSERT
                columns = ', '.join(lead_data.keys())
                placeholders = ', '.join(['%s'] * len(lead_data))
                
                cur.execute(f"""
                    INSERT INTO marketing_leads ({columns}, created_at, updated_at)
                    VALUES ({placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, list(lead_data.values()))
            
            success_count += 1
            
            # 진행 상황 표시
            if success_count % 20 == 0:
                print(f"  처리 중... {success_count}개 완료")
                conn.commit()  # 중간 커밋
            
        except Exception as e:
            error_count += 1
            print(f"❌ 행 {idx+2} 처리 중 오류: {str(e)}")
            conn.rollback()
            continue
    
    # 최종 커밋
    conn.commit()
    
    # 결과 확인
    cur.execute("SELECT COUNT(*) FROM marketing_leads")
    total_count = cur.fetchone()[0]
    
    # 샘플 데이터 확인
    cur.execute("""
        SELECT name, phone, age, revenue, lead_date 
        FROM marketing_leads 
        ORDER BY lead_id DESC 
        LIMIT 5
    """)
    samples = cur.fetchall()
    
    print(f"\n✅ 유입고객 데이터 시드 완료!")
    print(f"   - 성공: {success_count}개")
    print(f"   - 실패: {error_count}개")
    print(f"   - 전체 레코드: {total_count}개")
    
    if samples:
        print(f"\n📋 최근 추가된 데이터 샘플:")
        for sample in samples:
            print(f"   - {sample[0]}, {sample[1]}, {sample[2]}세, {sample[3]:,}원")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()