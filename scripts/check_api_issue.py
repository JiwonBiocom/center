#!/usr/bin/env python3
"""
API 문제 진단
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_issue():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 패키지 확인
    cursor.execute("SELECT COUNT(*) FROM packages")
    pkg_count = cursor.fetchone()[0]
    print(f"📦 패키지 수: {pkg_count}개")
    
    if pkg_count > 0:
        cursor.execute("SELECT package_id, package_name, base_price FROM packages LIMIT 3")
        print("패키지 샘플:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}. {row[1]} (₩{row[2]:,})")
    
    # 고객 확인
    cursor.execute("SELECT COUNT(*) FROM customers")
    cust_count = cursor.fetchone()[0]
    print(f"\n👥 고객 수: {cust_count}명")
    
    cursor.execute("SELECT customer_id, name, assigned_staff, first_visit_date FROM customers LIMIT 3")
    print("고객 샘플:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}. {row[1]} / 담당자: {row[2]} / 첫방문: {row[3]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_issue()