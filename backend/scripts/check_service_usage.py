#!/usr/bin/env python3
"""
서비스 이용 데이터 확인 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from datetime import datetime, date, timedelta
from core.config import settings

engine = create_engine(settings.DATABASE_URL)

def check_service_usage():
    """서비스 이용 데이터 확인"""

    with engine.connect() as conn:
        print("=== 서비스 이용 데이터 확인 ===\n")

        # 1. service_usage 테이블 전체 데이터 수
        total_count = conn.execute(text("""
            SELECT COUNT(*) FROM service_usage
        """)).scalar()
        print(f"전체 서비스 이용 기록: {total_count}건\n")

        # 2. 최근 30일 데이터
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_count = conn.execute(text("""
            SELECT COUNT(*)
            FROM service_usage
            WHERE service_date >= :date
        """), {"date": thirty_days_ago}).scalar()
        print(f"최근 30일 이용 기록: {recent_count}건\n")

        # 3. 서비스별 이용 현황
        print("서비스별 이용 현황 (최근 30일):")
        service_stats = conn.execute(text("""
            SELECT
                st.service_name,
                COUNT(su.usage_id) as usage_count
            FROM service_types st
            LEFT JOIN service_usage su ON st.service_type_id = su.service_type_id
                AND su.service_date >= :date
            GROUP BY st.service_type_id, st.service_name
            ORDER BY usage_count DESC
        """), {"date": thirty_days_ago})

        for row in service_stats:
            print(f"  - {row[0]}: {row[1]}건")

        # 4. 가장 최근 이용 기록
        print("\n가장 최근 서비스 이용 기록:")
        recent_usage = conn.execute(text("""
            SELECT
                su.service_date,
                c.name as customer_name,
                st.service_name
            FROM service_usage su
            JOIN customers c ON su.customer_id = c.customer_id
            JOIN service_types st ON su.service_type_id = st.service_type_id
            ORDER BY su.service_date DESC
            LIMIT 5
        """))

        for row in recent_usage:
            print(f"  - {row[0]}: {row[1]} - {row[2]}")

        # 5. 예약과 서비스 이용 연결 확인
        print("\n\n=== 예약 데이터와 비교 ===")

        # 완료된 예약 수
        completed_reservations = conn.execute(text("""
            SELECT COUNT(*)
            FROM reservations
            WHERE status = 'completed'
        """)).scalar()
        print(f"완료된 예약 수: {completed_reservations}건")

        # 서비스 이용 기록이 없는 완료된 예약
        print("\n완료된 예약 중 서비스 이용 기록이 없는 건수 확인...")
        missing_usage = conn.execute(text("""
            SELECT COUNT(*)
            FROM reservations r
            WHERE r.status = 'completed'
            AND NOT EXISTS (
                SELECT 1
                FROM service_usage su
                WHERE su.customer_id = r.customer_id
                AND su.service_type_id = r.service_type_id
                AND su.service_date = r.reservation_date
            )
        """)).scalar()
        print(f"서비스 이용 기록이 누락된 완료 예약: {missing_usage}건")

if __name__ == "__main__":
    check_service_usage()
