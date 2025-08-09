#!/usr/bin/env python3
"""
모든 마스터 데이터 한 번에 마이그레이션
1. service_types
2. packages  
3. kit_types
4. 고객 추가분
5. marketing_leads
"""
import sqlite3
import psycopg2
from pathlib import Path
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def migrate_all_master_data():
    """모든 마스터 데이터 마이그레이션"""
    
    print("🚀 전체 마스터 데이터 마이그레이션")
    print("=" * 80)
    print("마이그레이션 대상:")
    print("1. Service Types (5개)")
    print("2. Packages (12개)")  
    print("3. Kit Types (5개)")
    print("4. 누락된 고객 (61명)")
    print("5. Marketing Leads (176개)")
    print("6. Payment staff 업데이트")
    print("=" * 80)
    
    # 로컬 DB 연결
    local_db = Path("backend/aibio_center.db")
    local_conn = sqlite3.connect(local_db)
    local_conn.row_factory = sqlite3.Row
    local_cursor = local_conn.cursor()
    
    # 원격 DB 연결
    remote_conn = psycopg2.connect(DATABASE_URL)
    remote_cursor = remote_conn.cursor()
    
    results = {}
    
    try:
        # 1. Service Types 마이그레이션
        print("\n📋 1. Service Types 마이그레이션")
        print("-" * 40)
        
        # 기존 데이터 확인
        remote_cursor.execute("SELECT COUNT(*) FROM service_types")
        existing = remote_cursor.fetchone()[0]
        
        if existing > 0:
            print(f"   기존 {existing}개 데이터가 있습니다. 건너뜁니다.")
            results['service_types'] = f"건너뜀 (기존 {existing}개)"
        else:
            local_cursor.execute("SELECT * FROM service_types")
            service_types = local_cursor.fetchall()
            
            for st in service_types:
                remote_cursor.execute("""
                    INSERT INTO service_types (service_type_id, service_name, description)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (service_type_id) DO NOTHING
                """, (st['service_type_id'], st['service_name'], st['description']))
            
            # 브레인 서비스 추가 (누락된 것으로 보임)
            remote_cursor.execute("""
                INSERT INTO service_types (service_type_id, service_name, description)
                VALUES (4, '브레인피드백', '뇌파 및 심박변이도 트레이닝')
                ON CONFLICT (service_type_id) DO NOTHING
            """)
            
            results['service_types'] = f"성공 ({len(service_types)+1}개)"
            print(f"   ✅ {len(service_types)+1}개 추가 완료")
        
        # 2. Packages 마이그레이션
        print("\n📦 2. Packages 마이그레이션")
        print("-" * 40)
        
        # 기존 데이터 삭제
        remote_cursor.execute("DELETE FROM packages")
        
        local_cursor.execute("SELECT * FROM packages")
        packages = local_cursor.fetchall()
        
        for pkg in packages:
            remote_cursor.execute("""
                INSERT INTO packages 
                (package_id, package_name, total_sessions, price, valid_days, 
                 description, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pkg['package_id'], pkg['package_name'], pkg['total_sessions'],
                float(pkg['price']), pkg['valid_days'], pkg['description'],
                bool(pkg['is_active']), pkg['created_at'] or datetime.now()
            ))
        
        results['packages'] = f"성공 ({len(packages)}개)"
        print(f"   ✅ {len(packages)}개 추가 완료")
        
        # 3. Kit Types 마이그레이션
        print("\n🧪 3. Kit Types 마이그레이션")
        print("-" * 40)
        
        local_cursor.execute("SELECT * FROM kit_types")
        kit_types = local_cursor.fetchall()
        
        for kt in kit_types:
            remote_cursor.execute("""
                INSERT INTO kit_types (name, code, description, price, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING
            """, (
                kt['name'], kt['code'], kt['description'],
                int(kt['price']), bool(kt['is_active'])
            ))
        
        results['kit_types'] = f"성공 ({len(kit_types)}개)"
        print(f"   ✅ {len(kit_types)}개 추가 완료")
        
        # 4. 누락된 고객 찾기
        print("\n👥 4. 누락된 고객 찾기")
        print("-" * 40)
        
        # 로컬 고객 ID 목록
        local_cursor.execute("SELECT customer_id FROM customers")
        local_customers = set(row[0] for row in local_cursor.fetchall())
        
        # 온라인 고객 ID 목록
        remote_cursor.execute("SELECT customer_id FROM customers")
        online_customers = set(row[0] for row in remote_cursor.fetchall())
        
        # 누락된 고객
        missing_customers = local_customers - online_customers
        
        if missing_customers:
            print(f"   발견된 누락 고객: {len(missing_customers)}명")
            
            # 누락된 고객 정보 가져오기
            placeholders = ','.join('?' * len(missing_customers))
            local_cursor.execute(f"""
                SELECT * FROM customers 
                WHERE customer_id IN ({placeholders})
            """, list(missing_customers))
            
            missing_data = local_cursor.fetchall()
            
            for customer in missing_data:
                remote_cursor.execute("""
                    INSERT INTO customers 
                    (customer_id, name, phone, email, birth_year, 
                     first_visit_date, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (customer_id) DO NOTHING
                """, (
                    customer['customer_id'], customer['name'], customer['phone'],
                    customer['email'], customer['birth_year'],
                    customer['first_visit_date'], customer['created_at']
                ))
            
            results['customers'] = f"성공 ({len(missing_customers)}명 추가)"
            print(f"   ✅ {len(missing_customers)}명 추가 완료")
        else:
            results['customers'] = "누락 없음"
            print("   ✅ 누락된 고객 없음")
        
        # 5. Marketing Leads 마이그레이션
        print("\n📞 5. Marketing Leads 마이그레이션")
        print("-" * 40)
        
        # 기존 데이터 확인
        remote_cursor.execute("SELECT COUNT(*) FROM leads")
        existing_leads = remote_cursor.fetchone()[0]
        
        if existing_leads > 0:
            print(f"   기존 {existing_leads}개 데이터가 있습니다.")
        
        local_cursor.execute("SELECT * FROM marketing_leads")
        leads = local_cursor.fetchall()
        
        added_leads = 0
        for lead in leads:
            try:
                remote_cursor.execute("""
                    INSERT INTO leads 
                    (name, phone, email, source, status, assigned_to,
                     first_contact_date, notes, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    lead['name'], lead['phone'], lead['email'],
                    lead['source'], lead['status'], lead['assigned_to'],
                    lead['first_contact_date'], lead['notes'], 
                    lead['created_at'] or datetime.now()
                ))
                if remote_cursor.rowcount > 0:
                    added_leads += 1
            except:
                pass
        
        results['leads'] = f"성공 ({added_leads}개 추가)"
        print(f"   ✅ {added_leads}개 추가 완료")
        
        # 6. Payment staff 업데이트
        print("\n💰 6. Payment staff 업데이트")
        print("-" * 40)
        
        remote_cursor.execute("""
            UPDATE payments 
            SET payment_staff = '직원'
            WHERE payment_staff IS NULL OR payment_staff = ''
        """)
        
        updated = remote_cursor.rowcount
        results['payment_staff'] = f"성공 ({updated}건 업데이트)"
        print(f"   ✅ {updated}건 업데이트 완료")
        
        # 커밋
        remote_conn.commit()
        
        # 최종 결과
        print("\n" + "=" * 80)
        print("🎉 마이그레이션 완료!")
        print("=" * 80)
        for key, value in results.items():
            print(f"   {key}: {value}")
        
        # 연결 종료
        local_conn.close()
        remote_cursor.close()
        remote_conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        remote_conn.rollback()
        return False

if __name__ == "__main__":
    print("⚠️  주의: 이 스크립트는 프로덕션 데이터를 변경합니다!")
    print("계속하시려면 'yes'를 입력하세요:")
    
    confirm = input().strip().lower()
    if confirm == 'yes':
        migrate_all_master_data()
    else:
        print("취소되었습니다.")