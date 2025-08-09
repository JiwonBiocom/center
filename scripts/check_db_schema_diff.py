#!/usr/bin/env python3
"""
데이터베이스 스키마 차이점 확인
ORM 모델과 실제 데이터베이스 스키마 비교
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# 데이터베이스 연결 정보
DB_CONFIG = {
    'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
    'password': 'bico6819!!'
}

def get_table_columns(conn, table_name):
    """특정 테이블의 컬럼 정보 조회"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        return cur.fetchall()

def check_schema_differences():
    """스키마 차이점 확인"""
    print("🔍 데이터베이스 스키마 차이점 확인")
    print("=" * 60)
    
    # 중요 테이블과 예상 컬럼들 (실제 DB 구조 기준 - 필수 컬럼만)
    expected_schemas = {
        'notifications': ['notification_id', 'user_id', 'type', 'title', 'message', 'is_read', 'created_at'],
        'customers': ['customer_id', 'name', 'phone', 'first_visit_date'],
        'payments': ['payment_id', 'customer_id', 'amount', 'payment_date'],
        'packages': ['package_id', 'package_name', 'total_sessions', 'valid_months', 'base_price'],
        'users': ['user_id', 'email', 'password_hash', 'name', 'role']
    }
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        for table_name, expected_columns in expected_schemas.items():
            print(f"\n📊 {table_name} 테이블 검사")
            print("-" * 40)
            
            # 실제 컬럼 조회
            actual_columns = get_table_columns(conn, table_name)
            
            if not actual_columns:
                print(f"❌ 테이블이 존재하지 않습니다!")
                continue
            
            actual_column_names = [col['column_name'] for col in actual_columns]
            
            # 누락된 컬럼 확인
            missing_columns = set(expected_columns) - set(actual_column_names)
            if missing_columns:
                print(f"❌ 누락된 컬럼: {', '.join(missing_columns)}")
            
            # 추가된 컬럼 확인
            extra_columns = set(actual_column_names) - set(expected_columns)
            if extra_columns:
                print(f"➕ 추가된 컬럼: {', '.join(extra_columns)}")
            
            # 전체 컬럼 출력
            print(f"📋 실제 컬럼 ({len(actual_columns)}개):")
            for col in actual_columns[:10]:  # 처음 10개만
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"   • {col['column_name']}: {col['data_type']} ({nullable})")
            
            if len(actual_columns) > 10:
                print(f"   ... 그리고 {len(actual_columns) - 10}개 더")
                
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        conn.close()

def fix_notifications_table():
    """notifications 테이블에 user_id 컬럼 추가"""
    print("\n\n🔧 notifications 테이블 수정 SQL")
    print("=" * 60)
    
    sql_commands = [
        """
-- 1. user_id 컬럼 추가 (nullable로 먼저 추가)
ALTER TABLE notifications 
ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- 2. 기본값 설정 (기존 데이터가 있다면)
UPDATE notifications 
SET user_id = 1 
WHERE user_id IS NULL;

-- 3. NOT NULL 제약 조건 추가
ALTER TABLE notifications 
ALTER COLUMN user_id SET NOT NULL;

-- 4. 외래 키 제약 조건 추가
ALTER TABLE notifications 
ADD CONSTRAINT fk_notifications_user 
FOREIGN KEY (user_id) REFERENCES users(user_id);

-- 5. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
ON notifications(user_id);
        """
    ]
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"\n-- SQL 명령 #{i}")
        print(sql.strip())

def main():
    """메인 실행 함수"""
    print("🏥 Supabase 데이터베이스 스키마 진단")
    print(f"🕐 실행 시간: {datetime.now()}")
    print("=" * 60)
    
    # 1. 스키마 차이점 확인
    check_schema_differences()
    
    # 2. 수정 SQL 생성
    fix_notifications_table()
    
    print("\n\n✅ 진단 완료!")
    print("위의 SQL을 Supabase SQL Editor에서 실행하여 스키마를 수정하세요.")

if __name__ == "__main__":
    main()