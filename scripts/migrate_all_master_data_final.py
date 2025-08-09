#!/usr/bin/env python3
"""
모든 마스터 데이터 한 번에 마이그레이션 (최종 수정 버전)
- packages: price → base_price, valid_days → valid_months 변환
- customers: email, birth_year 없음
- leads 테이블 없음
"""
import sqlite3
import psycopg2
from pathlib import Path
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def migrate_all_master_data_final():
    """모든 마스터 데이터 마이그레이션 (최종 버전)"""
    
    print("🚀 전체 마스터 데이터 마이그레이션 (Final)")
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
        # 1. Service Types 마이그레이션 - 이미 있으므로 건너뜀
        results['service_types'] = "건너뜀 (기존 7개)"
        
        # 2. Packages 마이그레이션
        print("\n📦 2. Packages 마이그레이션")
        print("-" * 40)
        
        # 기존 데이터 확인
        remote_cursor.execute("SELECT COUNT(*) FROM packages")
        existing_packages = remote_cursor.fetchone()[0]
        
        if existing_packages > 0:
            print(f"   기존 {existing_packages}개 패키지가 있습니다.")
            results['packages'] = f"건너뜀 (기존 {existing_packages}개)"
        else:
            local_cursor.execute("SELECT * FROM packages")
            packages = local_cursor.fetchall()
            
            success_count = 0
            for pkg in packages:
                try:
                    # valid_days를 months로 변환 (30일 = 1개월)
                    valid_months = pkg['valid_days'] // 30
                    
                    remote_cursor.execute("""
                        INSERT INTO packages 
                        (package_id, package_name, total_sessions, base_price, valid_months, 
                         description, is_active, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        pkg['package_id'], 
                        pkg['package_name'], 
                        pkg['total_sessions'],
                        int(pkg['price']),  # base_price로 매핑
                        valid_months,       # valid_months로 변환
                        pkg['description'],
                        bool(pkg['is_active']), 
                        pkg['created_at'] or datetime.now()
                    ))
                    success_count += 1
                    print(f"   ✅ {pkg['package_name']} 추가")
                except Exception as e:
                    print(f"   ❌ {pkg['package_name']} 실패: {e}")
            
            # 시퀀스 재설정
            remote_cursor.execute("""
                SELECT setval('packages_package_id_seq', 
                             (SELECT COALESCE(MAX(package_id), 0) FROM packages), true)
            """)
            
            results['packages'] = f"성공 ({success_count}개)"
        
        # 3. Kit Types 마이그레이션
        print("\n🧪 3. Kit Types 마이그레이션")
        print("-" * 40)
        
        # 기존 데이터 확인
        remote_cursor.execute("SELECT COUNT(*) FROM kit_types")
        existing_kits = remote_cursor.fetchone()[0]
        
        if existing_kits > 0:
            print(f"   기존 {existing_kits}개 데이터가 있습니다.")
            results['kit_types'] = f"건너뜀 (기존 {existing_kits}개)"
        else:
            local_cursor.execute("SELECT * FROM kit_types")
            kit_types = local_cursor.fetchall()
            
            kit_count = 0
            for kt in kit_types:
                try:
                    remote_cursor.execute("""
                        INSERT INTO kit_types (name, code, description, price, is_active)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (code) DO UPDATE SET
                            name = EXCLUDED.name,
                            price = EXCLUDED.price
                    """, (
                        kt['name'], 
                        kt['code'], 
                        kt['description'],
                        int(kt['price']), 
                        bool(kt['is_active'])
                    ))
                    if remote_cursor.rowcount > 0:
                        kit_count += 1
                except Exception as e:
                    print(f"   ❌ {kt['name']} 실패: {e}")
            
            results['kit_types'] = f"성공 ({kit_count}개)"
            print(f"   ✅ {kit_count}개 추가/업데이트")
        
        # 4. 누락된 고객 찾기
        print("\n👥 4. 누락된 고객 추가")
        print("-" * 40)
        
        # 로컬 고객 전체 가져오기 (실제 컬럼만)
        local_cursor.execute("""
            SELECT customer_id, name, phone, first_visit_date, region,
                   referral_source, health_concerns, notes, assigned_staff, created_at
            FROM customers
        """)
        local_customers = local_cursor.fetchall()
        
        # 온라인에 없는 고객만 추가
        added_customers = 0
        for customer in local_customers:
            try:
                remote_cursor.execute("""
                    INSERT INTO customers 
                    (customer_id, name, phone, first_visit_date, region,
                     referral_source, health_concerns, notes, assigned_staff, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (customer_id) DO NOTHING
                """, (
                    customer['customer_id'], 
                    customer['name'], 
                    customer['phone'],
                    customer['first_visit_date'], 
                    customer['region'],
                    customer['referral_source'],
                    customer['health_concerns'],
                    customer['notes'],
                    customer['assigned_staff'],
                    customer['created_at'] or datetime.now()
                ))
                if remote_cursor.rowcount > 0:
                    added_customers += 1
            except Exception as e:
                print(f"   ❌ 고객 {customer['name']} 실패: {e}")
        
        results['customers'] = f"성공 ({added_customers}명 추가)"
        print(f"   ✅ {added_customers}명 새로 추가")
        
        # 5. Marketing Leads - leads 테이블이 없으므로 건너뜀
        results['leads'] = "leads 테이블 없음"
        
        # 6. Payment staff 업데이트
        print("\n💰 6. Payment staff 업데이트")
        print("-" * 40)
        
        # payment_staff 컬럼 존재 여부 확인
        remote_cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'payments' AND column_name = 'payment_staff'
            )
        """)
        
        if remote_cursor.fetchone()[0]:
            remote_cursor.execute("""
                UPDATE payments 
                SET payment_staff = '직원'
                WHERE payment_staff IS NULL OR payment_staff = ''
            """)
            updated = remote_cursor.rowcount
            results['payment_staff'] = f"성공 ({updated}건)"
            print(f"   ✅ {updated}건 업데이트")
        else:
            # 컬럼이 없으면 추가
            try:
                remote_cursor.execute("""
                    ALTER TABLE payments 
                    ADD COLUMN payment_staff VARCHAR(50)
                """)
                remote_cursor.execute("""
                    UPDATE payments SET payment_staff = '직원'
                """)
                results['payment_staff'] = "컬럼 추가 후 업데이트 성공"
                print("   ✅ payment_staff 컬럼 추가 및 업데이트 완료")
            except:
                results['payment_staff'] = "payment_staff 컬럼 없음"
                print("   ⚠️  payment_staff 컬럼을 추가할 수 없습니다.")
        
        # 커밋
        remote_conn.commit()
        
        # 최종 검증
        print("\n" + "=" * 80)
        print("📊 마이그레이션 결과 검증")
        print("=" * 80)
        
        # 패키지 확인
        remote_cursor.execute("SELECT COUNT(*), SUM(base_price) FROM packages WHERE is_active = true")
        pkg_count, total_price = remote_cursor.fetchone()
        print(f"✅ 패키지: {pkg_count}개 (총 가격: ₩{total_price:,.0f})")
        
        # 고객 확인
        remote_cursor.execute("SELECT COUNT(*) FROM customers")
        cust_count = remote_cursor.fetchone()[0]
        print(f"✅ 고객: {cust_count}명")
        
        # 키트 확인
        remote_cursor.execute("SELECT COUNT(*) FROM kit_types")
        kit_count = remote_cursor.fetchone()[0]
        print(f"✅ 키트 타입: {kit_count}개")
        
        # 결제 확인
        remote_cursor.execute("SELECT COUNT(*) FROM payments")
        payment_count = remote_cursor.fetchone()[0]
        print(f"✅ 결제: {payment_count}건")
        
        print("\n🎉 마이그레이션 완료!")
        print("-" * 80)
        for key, value in results.items():
            print(f"   {key}: {value}")
        
        # 연결 종료
        local_conn.close()
        remote_cursor.close()
        remote_conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        remote_conn.rollback()
        return False

if __name__ == "__main__":
    migrate_all_master_data_final()