#!/usr/bin/env python3
"""
마이그레이션 결과 확인
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_migration():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 패키지 확인
    cursor.execute('SELECT package_id, package_name, base_price FROM packages ORDER BY package_id')
    packages = cursor.fetchall()
    print('📦 패키지 목록:')
    for p in packages:
        print(f'  {p[0]}. {p[1]} - ₩{p[2]:,}')
    
    # 고객 수 확인
    cursor.execute('SELECT COUNT(*) FROM customers')
    print(f'\n👥 전체 고객 수: {cursor.fetchone()[0]}명')
    
    # 키트 타입 확인
    cursor.execute('SELECT name, price FROM kit_types')
    kits = cursor.fetchall()
    print('\n🧪 키트 타입:')
    for k in kits:
        print(f'  - {k[0]} - ₩{k[1]:,}')
    
    # payment_staff 확인
    cursor.execute("SELECT COUNT(*) FROM payments WHERE payment_staff = '직원'")
    print(f'\n💰 담당자 설정된 결제: {cursor.fetchone()[0]}건')
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_migration()