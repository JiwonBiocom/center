#!/usr/bin/env python3
"""
유입고객(marketing_leads) 데이터를 프로덕션 DB에 시드하는 스크립트
GitHub Actions에서 자동 실행됨
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
    # 숫자만 추출
    phone = re.sub(r'[^\d]', '', phone)
    
    # 10자리 또는 11자리만 유효
    if len(phone) in [10, 11]:
        # 하이픈 형식으로 변환
        if len(phone) == 10:
            return f"010-{phone[3:7]}-{phone[7:]}"
        else:
            return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    
    return None

def parse_date(date_value):
    """엑셀 날짜 값을 파싱"""
    if pd.isna(date_value):
        return None
    
    # pandas가 자동으로 datetime으로 변환한 경우
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()
    
    # 문자열인 경우
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
    """매출 금액 파싱"""
    if pd.isna(value):
        return 0
    
    if isinstance(value, (int, float)):
        return int(value)
    
    # 문자열에서 숫자만 추출
    value_str = str(value).replace(',', '').replace('원', '')
    try:
        return int(re.sub(r'[^\d]', '', value_str))
    except:
        return 0

def main():
    print("🚀 유입고객 데이터 시드 시작...")
    
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
    
    # 기존 테스트 데이터 삭제
    print("🧹 기존 테스트 데이터 정리 중...")
    test_patterns = ['테스트', 'test', 'Test', 'TEST', '샘플', 'sample']
    for pattern in test_patterns:
        cur.execute("""
            DELETE FROM marketing_leads 
            WHERE lead_name LIKE %s OR notes LIKE %s
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
                WHERE lead_name = %s AND lead_phone = %s
            """, (name, phone))
            
            existing = cur.fetchone()
            
            lead_data = {
                'lead_name': str(name).strip(),
                'lead_phone': phone,
                'age': row.get('나이', row.get('age')),
                'region': row.get('거주지역', row.get('region')),
                'lead_source': row.get('유입경로', row.get('lead_source', row.get('lead_channel'))),
                'marketing_channel': row.get('마케팅채널', row.get('marketing_channel')),
                'ad_content': row.get('시청 광고', row.get('ad_content', row.get('ad_watched'))),
                'ab_test_group': row.get('A/B 테스트', row.get('ab_test_group')),
                'lead_date': parse_date(row.get('DB입력일', row.get('lead_date', row.get('db_entry_date')))),
                'phone_consultation_date': parse_date(row.get('전화상담일', row.get('phone_consultation_date', row.get('phone_consult_date')))),
                'visit_consultation_date': parse_date(row.get('방문상담일', row.get('visit_consultation_date', row.get('visit_consult_date')))),
                'registration_date': parse_date(row.get('등록일', row.get('registration_date'))),
                'purchased_product': row.get('구매상품', row.get('purchased_product')),
                'revenue': parse_revenue(row.get('매출', row.get('revenue'))),
                'no_registration_reason': row.get('미등록사유', row.get('no_registration_reason')),
                'notes': row.get('비고', row.get('notes')),
                'lead_status': row.get('상태', row.get('lead_status', 'new'))
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
            
        except Exception as e:
            error_count += 1
            print(f"❌ 행 {idx+2} 처리 중 오류: {str(e)}")
            conn.rollback()
            continue
    
    # 커밋
    conn.commit()
    
    # 결과 확인
    cur.execute("SELECT COUNT(*) FROM marketing_leads")
    total_count = cur.fetchone()[0]
    
    print(f"\n✅ 유입고객 데이터 시드 완료!")
    print(f"   - 성공: {success_count}개")
    print(f"   - 실패: {error_count}개")
    print(f"   - 전체 레코드: {total_count}개")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()