#!/usr/bin/env python3
"""
빠른 스키마 수정 스크립트
현재 알려진 문제를 즉시 수정하는 SQL 생성
"""

import os
from datetime import datetime

# 알려진 스키마 문제들
KNOWN_FIXES = [
    # notifications 테이블 수정
    "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS user_id INTEGER;",
    "UPDATE notifications SET user_id = 1 WHERE user_id IS NULL;",
    "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);",
    
    # packages 테이블은 이미 수정됨 (price -> base_price)
    # "ALTER TABLE packages RENAME COLUMN price TO base_price;",
    # "ALTER TABLE packages RENAME COLUMN valid_days TO valid_months;",
]

def main():
    print("🔧 Quick Schema Fix SQL Generator")
    print("=" * 50)
    print("\n📝 Generated SQL Commands:\n")
    
    # SQL 파일 생성
    sql_filename = f"schema_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    with open(sql_filename, 'w') as f:
        f.write("-- Auto-generated schema fix SQL\n")
        f.write(f"-- Generated at: {datetime.now().isoformat()}\n")
        f.write("-- Run this in Supabase SQL Editor\n\n")
        
        for sql in KNOWN_FIXES:
            print(sql)
            f.write(sql + "\n")
        
        # 확인 쿼리 추가
        f.write("\n-- Verification queries\n")
        f.write("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'notifications' AND column_name = 'user_id';\n")
        f.write("SELECT COUNT(*) as notifications_with_user_id FROM notifications WHERE user_id IS NOT NULL;\n")
    
    print(f"\n✅ SQL saved to: {sql_filename}")
    print("\n📋 Next steps:")
    print("1. Copy the SQL above")
    print("2. Go to Supabase SQL Editor")
    print("3. Paste and execute")
    print("4. Verify the changes")
    
    # GitHub Actions 환경에서는 추가 출력
    if os.getenv("GITHUB_ACTIONS"):
        print(f"\n::set-output name=sql_file::{sql_filename}")
        with open(sql_filename, 'r') as f:
            print(f"::set-output name=sql_content::{f.read()}")

if __name__ == "__main__":
    main()