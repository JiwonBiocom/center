#!/usr/bin/env python3
"""
notifications 모델을 실제 DB와 일치시키기 위한 분석
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def analyze_notifications_table():
    """notifications 테이블 구조 상세 분석"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🔍 notifications 테이블 상세 분석")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    # 테이블 컬럼 확인
    cursor.execute("""
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'notifications'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    print(f"\n📋 실제 DB 컬럼 구조:")
    print(f"{'컬럼명':<20} {'데이터타입':<20} {'NULL여부':<10} {'기본값':<30}")
    print("-" * 80)
    
    for col in columns:
        nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
        default = str(col[3]) if col[3] else "-"
        if len(default) > 30:
            default = default[:27] + "..."
        print(f"{col[0]:<20} {col[1]:<20} {nullable:<10} {default:<30}")
    
    print(f"\n📝 모델 수정 제안:")
    print("```python")
    print("# models/notification.py 수정 필요 사항:")
    print()
    
    # DB에만 있는 컬럼들
    db_only_columns = ['customer_id', 'scheduled_at', 'sent_at', 'status', 'error_message', 'template_id', 'created_by']
    model_only_columns = ['is_sent', 'priority', 'action_url', 'related_id', 'read_at', 'scheduled_for']
    
    print("# DB에 있지만 모델에 없는 컬럼 추가:")
    for col in db_only_columns:
        print(f"# - {col}")
    
    print("\n# 모델에만 있는 컬럼 (제거 또는 DB에 추가):")
    for col in model_only_columns:
        print(f"# - {col}")
    
    print("\n# 컬럼명 변경:")
    print("# - scheduled_for → scheduled_at")
    print("# - is_sent (Boolean) → sent_at (DateTime)")
    print("```")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    analyze_notifications_table()