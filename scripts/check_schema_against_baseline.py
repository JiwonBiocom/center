#!/usr/bin/env python3
"""
Schema baseline과 현재 DB 비교
차이점이 있으면 자동 PR을 위한 플래그 생성
"""
import psycopg2
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# GitHub Actions에서는 환경변수 사용
DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres")

# 🔧 스키마 드리프트 예외 규칙 (TJ님 제안 적용)
IGNORE_TABLE_PATTERNS = [
    r"^staging_.*",           # staging으로 시작하는 모든 테이블
    r".*_backup$",            # _backup으로 끝나는 모든 테이블  
    r"^payment_staff_changes$", # 특정 로그 테이블
    r"^.*_additional_backup$", # 추가 백업 테이블들
    r"^temp_.*",              # 임시 테이블들
    r"^archive_.*"            # 아카이브 테이블들
]

def should_ignore_table(table_name):
    """테이블이 무시 대상인지 확인"""
    for pattern in IGNORE_TABLE_PATTERNS:
        if re.match(pattern, table_name):
            return True
    return False

def get_current_schema(conn):
    """현재 DB 스키마 조회"""
    schema = {}
    
    with conn.cursor() as cur:
        # 모든 테이블 조회
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        for table in tables:
            # 🔧 예외 규칙 적용: 무시할 테이블은 건너뛰기
            if should_ignore_table(table):
                print(f"⏭️  Ignoring table: {table} (matches exclusion pattern)")
                continue
                
            cur.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY ordinal_position
            """, (table,))
            
            columns = []
            for row in cur.fetchall():
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES'
                })
            
            schema[table] = columns
    
    return schema

def compare_schemas(baseline, current):
    """스키마 비교"""
    differences = {
        'added_tables': [],
        'removed_tables': [],
        'modified_tables': {},
        'ignored_tables': []
    }
    
    # 🔧 예외 테이블 필터링 적용
    baseline_tables = set()
    for table in baseline.get('tables', {}).keys():
        if should_ignore_table(table):
            differences['ignored_tables'].append(table)
        else:
            baseline_tables.add(table)
    
    current_tables = set(current.keys())  # current는 이미 필터링됨
    
    # 추가된 테이블 (예외 테이블 제외)
    added_tables = current_tables - baseline_tables
    differences['added_tables'] = [t for t in added_tables if not should_ignore_table(t)]
    
    # 제거된 테이블 (예외 테이블 제외) 
    removed_tables = baseline_tables - current_tables
    differences['removed_tables'] = [t for t in removed_tables if not should_ignore_table(t)]
    
    # 수정된 테이블
    for table in baseline_tables & current_tables:
        baseline_cols = {col['name'] for col in baseline['tables'][table]['columns']}
        current_cols = {col['name'] for col in current[table]}
        
        added_cols = current_cols - baseline_cols
        removed_cols = baseline_cols - current_cols
        
        if added_cols or removed_cols:
            differences['modified_tables'][table] = {
                'added_columns': list(added_cols),
                'removed_columns': list(removed_cols)
            }
    
    return differences

def main():
    # Baseline 로드
    baseline_path = Path(__file__).parent.parent / 'ci' / 'schema_baseline.json'
    
    if not baseline_path.exists():
        print("❌ schema_baseline.json not found!")
        print("Run: python scripts/generate_schema_baseline.py")
        sys.exit(1)
    
    with open(baseline_path, 'r') as f:
        baseline = json.load(f)
    
    # 현재 스키마 조회
    conn = psycopg2.connect(DATABASE_URL)
    try:
        current = get_current_schema(conn)
    finally:
        conn.close()
    
    # 비교
    differences = compare_schemas(baseline, current)
    
    # 차이점이 있는지 확인
    has_drift = (
        differences['added_tables'] or 
        differences['removed_tables'] or 
        differences['modified_tables']
    )
    
    if has_drift:
        print("⚠️ Schema drift detected!")
        
        # 리포트 생성
        report = ["## 🔍 Schema Drift Report\n"]
        report.append(f"Generated at: {datetime.now().isoformat()}\n")
        
        # 🔧 무시된 테이블 정보 추가
        if differences.get('ignored_tables'):
            report.append("### ⏭️ Ignored Tables (Excluded from Drift Detection)")
            for table in differences['ignored_tables']:
                matching_pattern = next((p for p in IGNORE_TABLE_PATTERNS if re.match(p, table)), "unknown")
                report.append(f"- `{table}` (pattern: `{matching_pattern}`)")
            report.append("")
        
        if differences['added_tables']:
            report.append("### ➕ Added Tables")
            for table in differences['added_tables']:
                report.append(f"- `{table}`")
            report.append("")
        
        if differences['removed_tables']:
            report.append("### ➖ Removed Tables")
            for table in differences['removed_tables']:
                report.append(f"- `{table}`")
            report.append("")
        
        if differences['modified_tables']:
            report.append("### 📝 Modified Tables")
            for table, changes in differences['modified_tables'].items():
                report.append(f"\n#### `{table}`")
                if changes['added_columns']:
                    report.append("- Added columns: " + ", ".join(f"`{col}`" for col in changes['added_columns']))
                if changes['removed_columns']:
                    report.append("- Removed columns: " + ", ".join(f"`{col}`" for col in changes['removed_columns']))
        
        # 리포트 저장
        report_content = '\n'.join(report)
        with open('schema_drift_report.md', 'w') as f:
            f.write(report_content)
        
        # 이메일 알림 발송
        try:
            recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', '').split(',')
            if recipients and recipients != [''] and os.path.exists('config/gmail_token.json'):
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from email_notifier import EmailNotifier
                notifier = EmailNotifier()
                notifier.send_schema_drift_alert(recipients, report_content)
        except Exception as e:
            print(f"⚠️ Failed to send email alert: {e}")
        
        # 플래그 파일 생성
        Path('schema_drift_detected.flag').touch()
        
        # 새 baseline 생성
        from generate_schema_baseline import generate_baseline
        generate_baseline()
        
        print("📝 Updated schema_baseline.json")
        sys.exit(0)  # PR 생성을 위해 정상 종료
    else:
        print("✅ No schema drift detected")
        sys.exit(0)

if __name__ == "__main__":
    main()