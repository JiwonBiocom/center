#!/usr/bin/env python3
"""
Customer 테이블 마이그레이션 실행 스크립트
안전한 트랜잭션 방식으로 처리
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

# 환경 변수 로드
load_dotenv()

def apply_migration(database_url=None):
    """Customer 테이블 마이그레이션 실행"""
    
    if not database_url:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL이 설정되지 않았습니다.")
            print("💡 사용법: python apply_migration.py 'postgresql://...'")
            return
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 마이그레이션 전 상태 확인...")
        
        # 현재 상태 확인
        check_query = """
        SELECT 
            COUNT(*) as total,
            COUNT(*) - COUNT(total_visits) as null_visits,
            COUNT(*) - COUNT(total_revenue) as null_revenue,
            COUNT(*) - COUNT(updated_at) as null_updated_at
        FROM customers;
        """
        cur.execute(check_query)
        before = cur.fetchone()
        
        print(f"전체 고객: {before['total']}명")
        print(f"NULL 값: visits={before['null_visits']}, revenue={before['null_revenue']}, updated_at={before['null_updated_at']}")
        
        if before['null_visits'] == 0 and before['null_revenue'] == 0 and before['null_updated_at'] == 0:
            print("✅ 이미 모든 데이터가 정리되어 있습니다.")
            cur.close()
            conn.close()
            return
        
        # 트랜잭션 시작
        print("\n🚀 마이그레이션 시작...")
        
        # 1. 기본값 설정
        print("1️⃣ 기본값 설정...")
        cur.execute("""
            ALTER TABLE customers
              ALTER COLUMN total_visits SET DEFAULT 0,
              ALTER COLUMN total_revenue SET DEFAULT 0,
              ALTER COLUMN updated_at SET DEFAULT now();
        """)
        
        # 2. NULL 값 업데이트
        print("2️⃣ NULL 값 업데이트...")
        
        # total_visits
        cur.execute("""
            UPDATE customers
            SET total_visits = 0
            WHERE total_visits IS NULL;
        """)
        visits_updated = cur.rowcount
        
        # total_revenue
        cur.execute("""
            UPDATE customers
            SET total_revenue = 0
            WHERE total_revenue IS NULL;
        """)
        revenue_updated = cur.rowcount
        
        # updated_at
        cur.execute("""
            UPDATE customers
            SET updated_at = created_at
            WHERE updated_at IS NULL;
        """)
        updated_at_updated = cur.rowcount
        
        # 결과 확인
        cur.execute(check_query)
        after = cur.fetchone()
        
        print(f"\n✅ 마이그레이션 완료!")
        print(f"- total_visits: {visits_updated}개 업데이트")
        print(f"- total_revenue: {revenue_updated}개 업데이트")
        print(f"- updated_at: {updated_at_updated}개 업데이트")
        print(f"\n최종 NULL 값: visits={after['null_visits']}, revenue={after['null_revenue']}, updated_at={after['null_updated_at']}")
        
        # 커밋
        conn.commit()
        print("\n✅ 변경사항이 저장되었습니다.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if 'conn' in locals():
            conn.rollback()
            print("⚠️ 변경사항이 롤백되었습니다.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        apply_migration(sys.argv[1])
    else:
        apply_migration()