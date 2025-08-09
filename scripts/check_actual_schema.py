#!/usr/bin/env python3
"""
실제 데이터베이스 스키마 확인
테이블 목록과 각 테이블의 컬럼 정보 확인
"""

import os
import sys
from pathlib import Path
import psycopg2
from tabulate import tabulate

# 프로젝트 경로 설정
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"

# .env 파일 로드
from dotenv import load_dotenv
env_path = backend_path / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_tables():
    """모든 테이블 목록 조회"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def get_table_info(table_name):
    """테이블의 컬럼 정보 조회"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            # 컬럼 정보
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            # 행 수
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
            except:
                row_count = "Error"
            
            return columns, row_count
    finally:
        conn.close()

def main():
    print("🔍 실제 데이터베이스 스키마 확인")
    print("="*80)
    
    # 테이블 목록
    tables = get_tables()
    print(f"\n📋 총 {len(tables)}개 테이블:")
    print("-"*80)
    
    # 테이블별 정보
    table_summary = []
    for table in tables:
        columns, row_count = get_table_info(table)
        table_summary.append([table, len(columns), row_count])
        
    print(tabulate(table_summary, headers=["테이블명", "컬럼 수", "행 수"], tablefmt="grid"))
    
    # 주요 테이블 상세 정보
    important_tables = ["customers", "payments", "packages", "services"]
    
    for table in important_tables:
        if table in tables:
            print(f"\n\n📊 {table} 테이블 구조:")
            print("-"*80)
            
            columns, _ = get_table_info(table)
            column_data = []
            for col in columns:
                name, dtype, max_len, nullable, default = col
                dtype_str = dtype
                if max_len:
                    dtype_str += f"({max_len})"
                
                column_data.append([
                    name,
                    dtype_str,
                    "NULL" if nullable == "YES" else "NOT NULL",
                    default if default else "-"
                ])
            
            print(tabulate(column_data, 
                          headers=["컬럼명", "타입", "NULL 허용", "기본값"], 
                          tablefmt="simple"))
    
    # 누락된 테이블 확인
    expected_tables = ["customers", "services", "packages", "payments", 
                      "users", "notifications", "customer_leads"]
    missing_tables = [t for t in expected_tables if t not in tables]
    
    if missing_tables:
        print(f"\n\n⚠️ 예상했지만 없는 테이블:")
        for table in missing_tables:
            print(f"   - {table}")
    
    # customers 테이블 샘플 데이터
    if "customers" in tables:
        conn = psycopg2.connect(DATABASE_URL)
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT customer_id, name, email, phone_number 
                    FROM customers 
                    LIMIT 5
                """)
                samples = cursor.fetchall()
                
                if samples:
                    print(f"\n\n📝 customers 테이블 샘플 데이터:")
                    print("-"*80)
                    print(tabulate(samples, 
                                  headers=["ID", "이름", "이메일", "전화번호"],
                                  tablefmt="simple"))
        finally:
            conn.close()

if __name__ == "__main__":
    main()