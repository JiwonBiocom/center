#!/usr/bin/env python3
"""
Supabase 데이터베이스 직접 연결 테스트
"""
import psycopg2

# Railway와 동일한 DATABASE_URL
DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_database():
    """데이터베이스 직접 확인"""
    
    print("🔍 Supabase 데이터베이스 직접 연결 테스트")
    print("=" * 50)
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 1. payments 테이블 확인
        print("\n1️⃣ payments 테이블 데이터 수:")
        cursor.execute("SELECT COUNT(*) FROM payments")
        count = cursor.fetchone()[0]
        print(f"   총 {count}건")
        
        # 2. 최근 데이터 확인
        if count > 0:
            print("\n2️⃣ 최근 결제 데이터 5건:")
            cursor.execute("""
                SELECT payment_id, customer_id, payment_date, amount, payment_method 
                FROM payments 
                ORDER BY payment_id DESC 
                LIMIT 5
            """)
            
            for row in cursor.fetchall():
                print(f"   ID:{row[0]} | 고객:{row[1]} | {row[2]} | ₩{row[3]:,.0f} | {row[4]}")
        
        # 3. 스키마 정보
        print("\n3️⃣ payments 테이블 컬럼:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'payments'
            ORDER BY ordinal_position
        """)
        
        for col in cursor.fetchall():
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # 4. payment_type enum 확인
        print("\n4️⃣ payment_type enum 값:")
        cursor.execute("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid FROM pg_type WHERE typname = 'payment_type'
            )
        """)
        
        enums = cursor.fetchall()
        if enums:
            for enum in enums:
                print(f"   - {enum[0]}")
        else:
            print("   payment_type enum이 없습니다")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    check_database()