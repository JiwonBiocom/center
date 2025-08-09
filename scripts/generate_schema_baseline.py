#!/usr/bin/env python3
"""
데이터베이스 스키마 baseline 생성
현재 DB 상태를 진실(source of truth)로 저장
"""
import psycopg2
import json
from datetime import datetime
from pathlib import Path

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def get_table_schema(conn, table_name):
    """테이블의 전체 스키마 정보 조회"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = []
        for row in cur.fetchall():
            columns.append({
                'name': row[0],
                'type': row[1],
                'nullable': row[2] == 'YES',
                'default': row[3],
                'max_length': row[4],
                'precision': row[5],
                'scale': row[6]
            })
        return columns

def get_all_tables(conn):
    """모든 테이블 목록 조회"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        return [row[0] for row in cur.fetchall()]

def generate_baseline():
    """스키마 baseline 생성"""
    print("🔍 데이터베이스 스키마 baseline 생성 중...")
    
    conn = psycopg2.connect(DATABASE_URL)
    
    try:
        baseline = {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'database': 'production',
            'tables': {}
        }
        
        tables = get_all_tables(conn)
        print(f"📊 {len(tables)}개 테이블 발견")
        
        for table in tables:
            print(f"  • {table} 처리 중...")
            columns = get_table_schema(conn, table)
            baseline['tables'][table] = {
                'columns': columns,
                'column_count': len(columns)
            }
        
        # ci 디렉토리 생성
        ci_dir = Path(__file__).parent.parent / 'ci'
        ci_dir.mkdir(exist_ok=True)
        
        # JSON 파일로 저장
        baseline_path = ci_dir / 'schema_baseline.json'
        with open(baseline_path, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Baseline 생성 완료: {baseline_path}")
        print(f"📋 총 {len(tables)}개 테이블, {sum(len(t['columns']) for t in baseline['tables'].values())}개 컬럼")
        
        return baseline_path
        
    finally:
        conn.close()

if __name__ == "__main__":
    generate_baseline()