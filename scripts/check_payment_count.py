#!/usr/bin/env python3
"""
결제 건수 카운트 확인 스크립트
"""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

# 환경 변수 로드
load_dotenv()

def check_payment_counts():
    """결제 건수 확인"""
    DATABASE_URL = "sqlite:///./backend/aibio_center.db"  # 백엔드 DB 사용
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. 전체 결제 건수 (중복 없이)
        result = conn.execute(text("""
            SELECT COUNT(DISTINCT payment_id) as total_payments
            FROM payments
        """)).fetchone()
        print(f"📊 전체 결제 건수 (DISTINCT): {result.total_payments}")
        
        # 2. 전체 결제 건수 (중복 포함)
        result = conn.execute(text("""
            SELECT COUNT(*) as total_rows
            FROM payments
        """)).fetchone()
        print(f"📊 전체 결제 행 수: {result.total_rows}")
        
        # 3. 중복 payment_id 확인
        result = conn.execute(text("""
            SELECT payment_id, COUNT(*) as cnt
            FROM payments
            GROUP BY payment_id
            HAVING COUNT(*) > 1
            LIMIT 10
        """)).fetchall()
        
        if result:
            print(f"\n⚠️  중복된 payment_id 발견:")
            for row in result:
                print(f"   - payment_id: {row.payment_id}, 중복 수: {row.cnt}")
        else:
            print(f"\n✅ 중복된 payment_id 없음")
        
        # 4. 날짜별 결제 건수
        result = conn.execute(text("""
            SELECT 
                payment_date,
                COUNT(DISTINCT payment_id) as distinct_count,
                COUNT(*) as total_count
            FROM payments
            WHERE payment_date >= date('now', '-7 days')
            GROUP BY payment_date
            ORDER BY payment_date DESC
        """)).fetchall()
        
        print(f"\n📅 최근 7일 날짜별 결제 건수:")
        for row in result:
            if row.distinct_count != row.total_count:
                print(f"   ⚠️  {row.payment_date}: DISTINCT={row.distinct_count}, TOTAL={row.total_count}")
            else:
                print(f"   ✅ {row.payment_date}: {row.distinct_count}건")

if __name__ == "__main__":
    check_payment_counts()