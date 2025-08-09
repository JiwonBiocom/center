#!/usr/bin/env python3
"""
미래 날짜 수정 (2026년 → 2024년)
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_future_dates():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 2026년 날짜를 가진 고객 확인
    cursor.execute("""
        SELECT customer_id, name, first_visit_date, last_visit_date
        FROM customers 
        WHERE first_visit_date >= '2026-01-01' 
           OR last_visit_date >= '2026-01-01'
    """)
    
    future_customers = cursor.fetchall()
    print(f"🔍 2026년 날짜를 가진 고객: {len(future_customers)}명")
    
    if future_customers:
        # 2026년을 2024년으로 변경
        cursor.execute("""
            UPDATE customers
            SET first_visit_date = first_visit_date - INTERVAL '2 years'
            WHERE first_visit_date >= '2026-01-01'
        """)
        first_updated = cursor.rowcount
        
        cursor.execute("""
            UPDATE customers
            SET last_visit_date = last_visit_date - INTERVAL '2 years'
            WHERE last_visit_date >= '2026-01-01'
        """)
        last_updated = cursor.rowcount
        
        print(f"✅ first_visit_date 수정: {first_updated}건")
        print(f"✅ last_visit_date 수정: {last_updated}건")
        
        # 다시 고객 상태 업데이트
        cursor.execute("""
            UPDATE customers
            SET customer_status = CASE
                WHEN last_visit_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'active'::customer_status
                WHEN last_visit_date >= CURRENT_DATE - INTERVAL '90 days' THEN 'inactive'::customer_status
                ELSE 'dormant'::customer_status
            END
            WHERE last_visit_date IS NOT NULL
        """)
        
        status_updated = cursor.rowcount
        print(f"✅ 고객 상태 재계산: {status_updated}명")
    
    # 최종 통계
    cursor.execute("""
        SELECT customer_status, COUNT(*) 
        FROM customers 
        GROUP BY customer_status
        ORDER BY customer_status
    """)
    
    print(f"\n📊 최종 고객 상태 분포:")
    print("-" * 40)
    for row in cursor.fetchall():
        status = row[0] or "(없음)"
        count = row[1]
        print(f"  {status}: {count}명")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_future_dates()