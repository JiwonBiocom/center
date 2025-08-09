#!/usr/bin/env python3
"""
로컬 결제 데이터를 Supabase 프로덕션 DB로 마이그레이션
실행: python scripts/migrate_payments_to_supabase.py
"""
import csv
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def get_database_url():
    """데이터베이스 URL 가져오기"""
    # Railway 환경 변수 우선
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Supabase 직접 연결 URL 구성
        db_host = os.getenv("SUPABASE_DB_HOST", "aws-0-ap-northeast-2.pooler.supabase.com")
        db_port = os.getenv("SUPABASE_DB_PORT", "6543")
        db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
        db_user = os.getenv("SUPABASE_DB_USER", "postgres.wvcxzyvmwwrbjpeuyvuh")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        
        if db_password:
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    return database_url

def convert_payment_method(method):
    """결제 방법 한글 -> 영문 변환"""
    method_map = {
        "카드": "card",
        "이체": "transfer",
        "현금": "cash"
    }
    return method_map.get(method, method.lower())

def migrate_payments():
    """결제 데이터 마이그레이션"""
    
    print("🚀 Supabase로 결제 데이터 마이그레이션 시작")
    print("=" * 50)
    
    # CSV 파일 경로
    csv_path = Path("backend/seed/local_payments_export.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return False
    
    # 데이터베이스 URL 가져오기
    database_url = get_database_url()
    
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        print("💡 .env 파일에 Supabase 연결 정보를 추가하세요:")
        print("   DATABASE_URL=postgresql://postgres.xxx:password@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres")
        return False
    
    try:
        # PostgreSQL 연결
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 현재 payments 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM payments")
        current_count = cursor.fetchone()[0]
        print(f"\n📊 현재 payments 테이블: {current_count}건")
        
        # CSV 데이터 읽기
        payments_data = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # payment_method 변환
                payment_method = convert_payment_method(row['payment_method'])
                
                payments_data.append((
                    int(row['customer_id']),
                    row['payment_date'],
                    float(row['amount']),
                    payment_method,
                    row['created_at'] if row['created_at'] else datetime.now().isoformat()
                ))
        
        print(f"\n📥 마이그레이션할 데이터: {len(payments_data)}건")
        
        # 중복 확인을 위한 기존 데이터 조회
        cursor.execute("""
            SELECT customer_id, payment_date, amount, payment_method 
            FROM payments
        """)
        existing_payments = set(cursor.fetchall())
        
        # 중복되지 않는 데이터만 필터링
        new_payments = []
        for payment in payments_data:
            check_tuple = (payment[0], payment[1], payment[2], payment[3])
            if check_tuple not in existing_payments:
                new_payments.append(payment)
        
        print(f"📋 중복 제외 후 추가할 데이터: {len(new_payments)}건")
        
        if len(new_payments) > 0:
            # 배치 삽입
            insert_query = """
                INSERT INTO payments (customer_id, payment_date, amount, payment_method, created_at)
                VALUES %s
            """
            
            execute_values(cursor, insert_query, new_payments)
            conn.commit()
            
            print(f"✅ {len(new_payments)}건의 결제 데이터 추가 완료!")
        else:
            print("ℹ️ 추가할 새로운 데이터가 없습니다.")
        
        # 최종 통계
        cursor.execute("""
            SELECT 
                COUNT(*) as total_count,
                COUNT(DISTINCT customer_id) as unique_customers,
                SUM(amount) as total_revenue,
                MIN(payment_date) as first_payment,
                MAX(payment_date) as last_payment
            FROM payments
        """)
        
        stats = cursor.fetchone()
        print("\n📈 최종 결제 데이터 통계:")
        print(f"  - 총 결제 건수: {stats[0]:,}건")
        print(f"  - 고유 고객 수: {stats[1]:,}명")
        print(f"  - 총 매출액: ₩{stats[2]:,.0f}")
        print(f"  - 첫 결제일: {stats[3]}")
        print(f"  - 마지막 결제일: {stats[4]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    success = migrate_payments()
    
    if success:
        print("\n🎉 마이그레이션 완료!")
        print("💡 확인 방법:")
        print("   - API: https://center-production-1421.up.railway.app/api/v1/payments/")
        print("   - UI: https://center-ten.vercel.app/payments")
    else:
        print("\n❌ 마이그레이션 실패!")
        print("💡 .env 파일에 DATABASE_URL을 설정하고 다시 시도하세요.")

if __name__ == "__main__":
    main()