#!/usr/bin/env python3
"""
Customer 테이블의 NULL 값 현황 확인
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

def check_customer_nulls():
    """Customer 테이블의 NULL 값 현황 확인"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # NULL 값 통계 조회
        query = """
        SELECT 
            COUNT(*) as total_customers,
            COUNT(total_visits) as with_visits,
            COUNT(total_revenue) as with_revenue,
            COUNT(updated_at) as with_updated_at,
            COUNT(*) - COUNT(total_visits) as null_visits,
            COUNT(*) - COUNT(total_revenue) as null_revenue,
            COUNT(*) - COUNT(updated_at) as null_updated_at
        FROM customers;
        """
        
        cur.execute(query)
        result = cur.fetchone()
        
        print("\n📊 Customer 테이블 NULL 값 현황")
        print("=" * 50)
        print(f"전체 고객 수: {result['total_customers']}")
        print(f"\nNULL 값 현황:")
        print(f"- total_visits NULL: {result['null_visits']}개")
        print(f"- total_revenue NULL: {result['null_revenue']}개")
        print(f"- updated_at NULL: {result['null_updated_at']}개")
        
        # 샘플 데이터 확인
        print("\n📋 NULL 값을 가진 샘플 데이터 (최대 5개):")
        sample_query = """
        SELECT customer_id, name, total_visits, total_revenue, updated_at
        FROM customers
        WHERE total_visits IS NULL 
           OR total_revenue IS NULL 
           OR updated_at IS NULL
        LIMIT 5;
        """
        
        cur.execute(sample_query)
        samples = cur.fetchall()
        
        for sample in samples:
            print(f"\nID: {sample['customer_id']}, 이름: {sample['name']}")
            print(f"  - total_visits: {sample['total_visits']}")
            print(f"  - total_revenue: {sample['total_revenue']}")
            print(f"  - updated_at: {sample['updated_at']}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_customer_nulls()