#!/usr/bin/env python3
"""
원본 엑셀(950명)과 비교하여 미반영 고객 식별
"""
import pandas as pd
import requests
from datetime import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/aibio_center")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def load_original_customers():
    """원본 엑셀 데이터 로드"""
    excel_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장_전체고객.csv"

    print("📋 원본 엑셀 데이터 로드 중...")
    df = pd.read_csv(excel_path, encoding='utf-8-sig')

    # 컬럼명 정리
    df.columns = df.columns.str.strip()

    # 이름과 전화번호 정리
    df['이름'] = df['이름'].str.strip()
    if '연락처' in df.columns:
        df['연락처'] = df['연락처'].astype(str).str.strip()
        # 전화번호 형식 통일
        df['연락처_정리'] = df['연락처'].str.replace('-', '').str.replace(' ', '')

    print(f"  ✅ 원본 고객 수: {len(df)}명")
    return df

def fetch_all_db_customers():
    """DB의 모든 고객 데이터 가져오기"""
    print("\n📊 DB 고객 데이터 가져오는 중...")

    all_customers = []
    skip = 0
    limit = 100

    while True:
        response = requests.get(f"http://localhost:8000/api/v1/customers",
                               params={"skip": skip, "limit": limit})
        data = response.json()

        customers = data.get("data", [])
        if not customers:
            break

        all_customers.extend(customers)
        skip += limit

        if len(all_customers) >= data.get("total", 0):
            break

    print(f"  ✅ DB 고객 수: {len(all_customers)}명")
    return all_customers

def identify_unreflected():
    """미반영 고객 식별"""
    print("\n🔍 미반영 고객 식별 시작")
    print("="*60)

    # 1. 데이터 로드
    original_df = load_original_customers()
    db_customers = fetch_all_db_customers()
    db_df = pd.DataFrame(db_customers)

    # 2. 매칭 작업
    print("\n🔍 매칭 작업 중...")

    # 원본 고객 이름 목록
    original_names = set(original_df['이름'].tolist())

    # 전화번호가 있는 경우 전화번호로도 매칭
    original_phones = set()
    if '연락처_정리' in original_df.columns:
        original_phones = set(original_df[original_df['연락처_정리'].notna()]['연락처_정리'].tolist())

    # DB 고객 중 원본에 없는 고객 찾기
    unreflected = []

    for _, customer in db_df.iterrows():
        # 이름으로 매칭
        is_original = customer['name'] in original_names

        # 전화번호로도 매칭 시도
        if not is_original and customer.get('phone'):
            phone_cleaned = str(customer['phone']).replace('-', '').replace(' ', '')
            if phone_cleaned in original_phones:
                is_original = True

        if not is_original:
            # 데이터 출처 추정
            created_date = pd.to_datetime(customer['created_at']).date()
            data_source = "Unknown"

            if created_date == pd.to_datetime('2025-06-05').date():
                data_source = "초기 마이그레이션 (6/5)"
            elif created_date == pd.to_datetime('2025-06-20').date():
                data_source = "2차 마이그레이션 (6/20) - 추가 데이터"
            elif created_date == pd.to_datetime('2025-06-25').date():
                data_source = "월별 이용현황 import (6/25)"
            elif created_date >= pd.to_datetime('2025-06-26').date():
                data_source = "수동 입력 또는 테스트 데이터"

            customer['data_source'] = data_source
            unreflected.append(customer)

    print(f"\n📊 식별 결과:")
    print(f"  - 원본 고객: {len(original_df)}명")
    print(f"  - DB 전체 고객: {len(db_df)}명")
    print(f"  - 미반영 고객: {len(unreflected)}명")

    # 데이터 출처별 통계
    if unreflected:
        unreflected_df = pd.DataFrame(unreflected)
        source_stats = unreflected_df['data_source'].value_counts()

        print(f"\n📊 미반영 고객 출처별 분포:")
        for source, count in source_stats.items():
            print(f"  - {source}: {count}명")

        # 결과 저장
        output_file = "/Users/vibetj/coding/center/unreflected_customers.csv"
        unreflected_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 미반영 고객 목록 저장: {output_file}")

    return unreflected

def create_migration_script(unreflected):
    """미반영 고객 마이그레이션 스크립트 생성"""
    if not unreflected:
        print("\n✅ 미반영 고객이 없습니다.")
        return

    print("\n📝 마이그레이션 SQL 스크립트 생성 중...")

    # 테이블 생성 SQL
    create_table_sql = """
-- 미반영 고객 테이블 생성
CREATE TABLE IF NOT EXISTS unreflected_customers (
    id SERIAL PRIMARY KEY,
    original_customer_id INTEGER,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    first_visit_date DATE,
    region VARCHAR(100),
    referral_source VARCHAR(100),
    health_concerns TEXT,
    notes TEXT,
    assigned_staff VARCHAR(50),
    birth_year INTEGER,
    gender VARCHAR(10),
    address TEXT,
    emergency_contact VARCHAR(20),
    occupation VARCHAR(100),
    data_source VARCHAR(200),
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_unreflected_name ON unreflected_customers(name);
CREATE INDEX IF NOT EXISTS idx_unreflected_phone ON unreflected_customers(phone);
CREATE INDEX IF NOT EXISTS idx_unreflected_status ON unreflected_customers(status);
"""

    # INSERT SQL 생성
    insert_sqls = []
    for customer in unreflected:
        values = []
        values.append(f"{customer.get('customer_id', 'NULL')}")  # original_customer_id
        values.append(f"'{customer['name'].replace("'", "''")}'")
        values.append(f"'{customer.get('phone', '')}'" if customer.get('phone') else "NULL")
        values.append(f"'{customer.get('email', '')}'" if customer.get('email') else "NULL")
        values.append(f"'{customer.get('first_visit_date')}'" if customer.get('first_visit_date') else "NULL")
        values.append(f"'{customer.get('region', '').replace("'", "''")}'" if customer.get('region') else "NULL")
        values.append(f"'{customer.get('referral_source', '').replace("'", "''")}'" if customer.get('referral_source') else "NULL")
        values.append(f"'{customer.get('health_concerns', '').replace("'", "''")}'" if customer.get('health_concerns') else "NULL")
        values.append(f"'{customer.get('notes', '').replace("'", "''")}'" if customer.get('notes') else "NULL")
        values.append(f"'{customer.get('assigned_staff', '').replace("'", "''")}'" if customer.get('assigned_staff') else "NULL")
        values.append(f"{customer.get('birth_year')}" if customer.get('birth_year') else "NULL")
        values.append(f"'{customer.get('gender', '')}'" if customer.get('gender') else "NULL")
        values.append(f"'{customer.get('address', '').replace("'", "''")}'" if customer.get('address') else "NULL")
        values.append(f"'{customer.get('emergency_contact', '')}'" if customer.get('emergency_contact') else "NULL")
        values.append(f"'{customer.get('occupation', '').replace("'", "''")}'" if customer.get('occupation') else "NULL")
        values.append(f"'{customer.get('data_source', 'Unknown')}'")
        values.append(f"'{customer.get('created_at')}'")

        insert_sql = f"""
INSERT INTO unreflected_customers (
    original_customer_id, name, phone, email, first_visit_date,
    region, referral_source, health_concerns, notes, assigned_staff,
    birth_year, gender, address, emergency_contact, occupation,
    data_source, import_date
) VALUES (
    {', '.join(values)}
);"""
        insert_sqls.append(insert_sql)

    # 스크립트 저장
    script_file = "/Users/vibetj/coding/center/migration_unreflected_customers.sql"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(create_table_sql)
        f.write("\n\n-- 미반영 고객 데이터 INSERT\n")
        f.write(''.join(insert_sqls))
        f.write(f"\n\n-- 총 {len(unreflected)}명의 미반영 고객 데이터")

    print(f"  ✅ 마이그레이션 스크립트 생성: {script_file}")

if __name__ == "__main__":
    unreflected = identify_unreflected()
    create_migration_script(unreflected)
