#!/usr/bin/env python3
"""
검사키트 수령(kit_receipts) 데이터를 프로덕션 DB에 시드하는 스크립트 - 수정 버전
실제 테이블 구조에 맞춰 수정됨
"""

import sys
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse, quote_plus
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

def get_or_create_customer(cur, name, phone=None):
    """고객 찾기 또는 생성"""
    # 전화번호로 먼저 찾기
    if phone:
        cur.execute("""
            SELECT customer_id FROM customers WHERE phone = %s
        """, (phone,))
        result = cur.fetchone()
        if result:
            return result[0]
    
    # 이름으로 찾기
    cur.execute("""
        SELECT customer_id FROM customers WHERE name = %s
    """, (name,))
    result = cur.fetchone()
    if result:
        return result[0]
    
    # 새로 생성
    cur.execute("""
        INSERT INTO customers (name, phone, created_at, updated_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING customer_id
    """, (name, phone))
    return cur.fetchone()[0]

def main():
    print("🚀 검사키트 수령 데이터 시드 시작 (수정 버전)...")
    
    # 환경 변수에서 DB 정보 가져오기
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # Excel 파일 경로
    excel_path = "backend/seed/kit_receipts.xlsx"
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
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'kit_receipts'
        ORDER BY ordinal_position
    """)
    columns = [row[0] for row in cur.fetchall()]
    print(f"발견된 컬럼: {', '.join(columns[:5])}...")
    
    # 기존 테스트 데이터 삭제
    print("\n🧹 기존 테스트 데이터 정리 중...")
    test_patterns = ['테스트', 'test', 'Test', 'TEST', '샘플', 'sample']
    for pattern in test_patterns:
        cur.execute("""
            SELECT kr.kit_receipt_id 
            FROM kit_receipts kr
            JOIN customers c ON kr.customer_id = c.customer_id
            WHERE c.name LIKE %s OR kr.notes LIKE %s
        """, (f'%{pattern}%', f'%{pattern}%'))
        
        test_ids = [row[0] for row in cur.fetchall()]
        if test_ids:
            cur.execute("""
                DELETE FROM kit_receipts WHERE kit_receipt_id = ANY(%s)
            """, (test_ids,))
    
    conn.commit()
    
    # 데이터 삽입/업데이트
    success_count = 0
    error_count = 0
    
    for idx, row in df.iterrows():
        try:
            # 필수 필드 확인
            name = row.get('고객명', row.get('name', row.get('customer_name')))
            if pd.isna(name) or not name:
                print(f"⚠️  행 {idx+2}: 고객명이 없습니다. 건너뜁니다.")
                continue
            
            # 전화번호 정리
            phone = clean_phone_number(row.get('연락처', row.get('phone', row.get('customer_phone'))))
            
            # 고객 ID 찾기 또는 생성
            customer_id = get_or_create_customer(cur, name, phone)
            
            # 키트 시리얼 번호
            serial = row.get('시리얼', row.get('serial', row.get('kit_serial')))
            if serial:
                serial = str(serial).strip()
            
            # 기존 레코드 확인 (시리얼 번호로)
            existing_id = None
            if serial:
                cur.execute("""
                    SELECT kit_receipt_id FROM kit_receipts 
                    WHERE kit_serial = %s
                """, (serial,))
                result = cur.fetchone()
                if result:
                    existing_id = result[0]
            
            # 데이터 준비 - 실제 컬럼명에 맞춰 수정
            kit_data = {
                'customer_id': customer_id,
                'name': str(name).strip(),
                'phone': phone,
                'kit_type': row.get('키트종류', row.get('kit_type', '장내미생물')),
                'kit_serial': serial,
                'received_date': parse_date(row.get('키트수령일', row.get('received_date'))),
                'result_date': parse_date(row.get('결과지수령일', row.get('result_date'))),
                'delivered_date': parse_date(row.get('결과지전달일', row.get('delivered_date'))),
                'status': row.get('상태', row.get('status', 'received')),
                'notes': row.get('비고', row.get('notes'))
            }
            
            # None 값 제거
            kit_data = {k: v for k, v in kit_data.items() if v is not None}
            
            if existing_id:
                # UPDATE
                kit_data_without_id = {k: v for k, v in kit_data.items() if k != 'customer_id'}
                set_clause = ', '.join([f"{k} = %s" for k in kit_data_without_id.keys()])
                values = list(kit_data_without_id.values()) + [existing_id]
                
                cur.execute(f"""
                    UPDATE kit_receipts 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE kit_receipt_id = %s
                """, values)
            else:
                # INSERT
                columns = ', '.join(kit_data.keys())
                placeholders = ', '.join(['%s'] * len(kit_data))
                
                cur.execute(f"""
                    INSERT INTO kit_receipts ({columns}, created_at, updated_at)
                    VALUES ({placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, list(kit_data.values()))
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"❌ 행 {idx+2} 처리 중 오류: {str(e)}")
            conn.rollback()
            continue
    
    # 커밋
    conn.commit()
    
    # 결과 확인
    cur.execute("SELECT COUNT(*) FROM kit_receipts")
    total_count = cur.fetchone()[0]
    
    print(f"\n✅ 검사키트 수령 데이터 시드 완료!")
    print(f"   - 성공: {success_count}개")
    print(f"   - 실패: {error_count}개")
    print(f"   - 전체 레코드: {total_count}개")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()