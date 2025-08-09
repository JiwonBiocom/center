#!/usr/bin/env python3
"""
예약 상태 enum 값 확인 스크립트
"""

import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/aibio_center")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("=== 예약 상태 Enum 값 확인 ===\n")

    # Enum 타입 확인
    result = conn.execute(text("""
        SELECT unnest(enum_range(NULL::reservationstatus)) AS enum_value
    """))

    print("DB에 정의된 ReservationStatus enum 값:")
    for row in result:
        print(f"  - {row[0]}")

    print("\n현재 예약 테이블의 status 값 분포:")
    status_dist = conn.execute(text("""
        SELECT status, COUNT(*) as count
        FROM reservations
        GROUP BY status
    """))

    for row in status_dist:
        print(f"  - {row[0]}: {row[1]}건")
