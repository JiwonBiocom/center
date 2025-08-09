#!/usr/bin/env python3
"""Railway 배포 환경의 스키마 문제 점검 스크립트"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# .env 파일 로드
load_dotenv()

# 환경변수에서 DB URL 가져오기
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    sys.exit(1)

print(f"Checking database schema at: {datetime.now()}")
print("=" * 60)

try:
    # 데이터베이스 연결
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # 모든 테이블 목록 가져오기
    tables = inspector.get_table_names()
    print(f"\nTotal tables found: {len(tables)}")
    
    # Railway 로그에서 언급된 문제들 체크
    issues = []
    
    # 1. notifications 테이블의 user_id 컬럼 체크
    if 'notifications' in tables:
        columns = {col['name']: col for col in inspector.get_columns('notifications')}
        if 'user_id' not in columns:
            issues.append("❌ notifications table missing 'user_id' column")
        else:
            print("✅ notifications table has 'user_id' column")
    else:
        issues.append("❌ notifications table not found")
    
    # 2. packages 테이블의 price/base_price 컬럼 체크
    if 'packages' in tables:
        columns = {col['name']: col for col in inspector.get_columns('packages')}
        if 'price' in columns:
            issues.append("❌ packages table still has 'price' column (should be 'base_price')")
        if 'base_price' not in columns:
            issues.append("❌ packages table missing 'base_price' column")
        else:
            print("✅ packages table has 'base_price' column")
    else:
        issues.append("❌ packages table not found")
    
    # 3. customer_payments 테이블 체크 (Railway 로그에서 언급됨)
    if 'customer_payments' in tables:
        print("⚠️  customer_payments table exists (might be legacy)")
        columns = inspector.get_columns('customer_payments')
        print(f"   Columns: {[col['name'] for col in columns]}")
    
    # 4. payments 테이블 체크
    if 'payments' in tables:
        columns = {col['name']: col for col in inspector.get_columns('payments')}
        print("✅ payments table exists")
        required_columns = ['payment_id', 'customer_id', 'payment_date', 'amount']
        for col in required_columns:
            if col not in columns:
                issues.append(f"❌ payments table missing '{col}' column")
    else:
        issues.append("❌ payments table not found")
    
    # 5. 기타 Railway 로그에서 언급된 테이블들 체크
    critical_tables = ['customers', 'services', 'service_usages', 'packages', 'package_purchases']
    for table in critical_tables:
        if table not in tables:
            issues.append(f"❌ {table} table not found")
        else:
            print(f"✅ {table} table exists")
    
    # 결과 출력
    print("\n" + "=" * 60)
    if issues:
        print("🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No schema issues found!")
    
    # SQL 스크립트 생성
    if issues:
        print("\n" + "=" * 60)
        print("📝 GENERATING FIX SQL...")
        
        fix_sql = []
        fix_sql.append("-- Railway Schema Fix SQL")
        fix_sql.append(f"-- Generated at: {datetime.now().isoformat()}")
        fix_sql.append("-- Run this in Supabase SQL Editor\n")
        
        # notifications user_id 수정
        if any("notifications" in issue and "user_id" in issue for issue in issues):
            fix_sql.append("-- Fix notifications table")
            fix_sql.append("ALTER TABLE notifications ADD COLUMN IF NOT EXISTS user_id INTEGER;")
            fix_sql.append("UPDATE notifications SET user_id = 1 WHERE user_id IS NULL;")
            fix_sql.append("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);\n")
        
        # packages price -> base_price 수정
        if any("packages" in issue and ("price" in issue or "base_price" in issue) for issue in issues):
            fix_sql.append("-- Fix packages table")
            fix_sql.append("ALTER TABLE packages RENAME COLUMN price TO base_price;")
            fix_sql.append("-- If above fails because column already renamed, ignore the error\n")
        
        # customer_payments 관련 처리
        if 'customer_payments' in tables:
            fix_sql.append("-- Handle legacy customer_payments table")
            fix_sql.append("-- Check if this table is still needed or can be dropped")
            fix_sql.append("-- SELECT COUNT(*) FROM customer_payments;\n")
        
        # 파일로 저장
        fix_filename = f"railway_schema_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        with open(fix_filename, 'w') as f:
            f.write('\n'.join(fix_sql))
        
        print(f"✅ Fix SQL saved to: {fix_filename}")
        print("\nSQL Preview:")
        print("-" * 40)
        print('\n'.join(fix_sql[:10]))  # 처음 10줄만 미리보기
        if len(fix_sql) > 10:
            print("... (more lines)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()