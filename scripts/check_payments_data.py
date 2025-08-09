#!/usr/bin/env python3
"""
Payments 테이블 데이터 확인
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

# 환경 변수 로드
load_dotenv()

def check_payments_data():
    """Payments 테이블 데이터 현황 확인"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 테이블 존재 여부 확인
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('payments', 'customers');
        """)
        tables = [row['table_name'] for row in cur.fetchall()]
        print(f"📋 존재하는 테이블: {tables}")
        
        if 'payments' not in tables:
            print("❌ payments 테이블이 존재하지 않습니다.")
            return
            
        if 'customers' not in tables:
            print("❌ customers 테이블이 존재하지 않습니다.")
            return
        
        # Payments 테이블 데이터 확인
        cur.execute("SELECT COUNT(*) as count FROM payments;")
        payments_count = cur.fetchone()['count']
        print(f"\n💰 결제 데이터: {payments_count}개")
        
        if payments_count > 0:
            # 샘플 데이터 확인
            cur.execute("""
                SELECT payment_id, customer_id, payment_date, amount, payment_method 
                FROM payments 
                ORDER BY payment_id DESC 
                LIMIT 3;
            """)
            samples = cur.fetchall()
            print("\n📋 최근 결제 데이터 (샘플):")
            for sample in samples:
                print(f"  ID: {sample['payment_id']}, 고객ID: {sample['customer_id']}, "
                      f"날짜: {sample['payment_date']}, 금액: {sample['amount']}, "
                      f"방법: {sample['payment_method']}")
            
            # JOIN 테스트
            print("\n🔗 Customer JOIN 테스트:")
            cur.execute("""
                SELECT p.payment_id, p.customer_id, c.name as customer_name
                FROM payments p
                LEFT JOIN customers c ON p.customer_id = c.customer_id
                LIMIT 3;
            """)
            join_samples = cur.fetchall()
            for sample in join_samples:
                print(f"  결제ID: {sample['payment_id']}, 고객ID: {sample['customer_id']}, "
                      f"고객명: {sample['customer_name']}")
        else:
            print("ℹ️ 결제 데이터가 없습니다.")
        
        # Customers 테이블 데이터 확인
        cur.execute("SELECT COUNT(*) as count FROM customers;")
        customers_count = cur.fetchone()['count']
        print(f"\n👥 고객 데이터: {customers_count}개")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_payments_data()