#!/usr/bin/env python3
"""
데이터베이스의 enum 값 확인 및 수정 스크립트
"""

import os
from sqlalchemy import create_engine, text
import sys

# Railway 환경에서도 동작하도록 DATABASE_URL 직접 사용
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

def check_enums():
    """현재 enum 상태 확인"""

    with engine.connect() as conn:
        print("=== 현재 Enum 상태 확인 ===\n")

        # ReservationStatus enum 값 확인
        try:
            result = conn.execute(text("""
                SELECT unnest(enum_range(NULL::reservationstatus)) AS enum_value
                ORDER BY enum_value
            """))
            values = [row[0] for row in result]

            print("ReservationStatus enum 값:")
            for v in values:
                print(f"  - {v}")

            # 대문자와 소문자 확인
            uppercase_values = [v for v in values if v.isupper()]
            lowercase_values = [v for v in values if v.islower()]

            print(f"\n대문자 값: {uppercase_values}")
            print(f"소문자 값: {lowercase_values}")

            # 현재 데이터 상태 확인
            print("\n=== 예약 데이터 상태 ===")
            status_count = conn.execute(text("""
                SELECT status, COUNT(*) as count
                FROM reservations
                GROUP BY status
                ORDER BY status
            """))

            for row in status_count:
                print(f"  {row[0]}: {row[1]}건")

            return uppercase_values, lowercase_values

        except Exception as e:
            print(f"오류 발생: {e}")
            return [], []

def remove_uppercase_enums():
    """대문자 enum 값 제거 (소문자만 남김)"""

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("\n=== Enum 정리 시작 ===")

            # 1. 대문자 데이터를 소문자로 변환
            print("\n1. 대문자 데이터를 소문자로 변환...")

            # PENDING -> pending
            updated = conn.execute(text("""
                UPDATE reservations
                SET status = 'pending'::reservationstatus
                WHERE status = 'PENDING'::reservationstatus
                RETURNING reservation_id
            """))
            count = len(updated.fetchall())
            print(f"   PENDING -> pending: {count}건 변환")

            # CONFIRMED -> confirmed
            updated = conn.execute(text("""
                UPDATE reservations
                SET status = 'confirmed'::reservationstatus
                WHERE status = 'CONFIRMED'::reservationstatus
                RETURNING reservation_id
            """))
            count = len(updated.fetchall())
            print(f"   CONFIRMED -> confirmed: {count}건 변환")

            # CANCELLED -> cancelled
            updated = conn.execute(text("""
                UPDATE reservations
                SET status = 'cancelled'::reservationstatus
                WHERE status = 'CANCELLED'::reservationstatus
                RETURNING reservation_id
            """))
            count = len(updated.fetchall())
            print(f"   CANCELLED -> cancelled: {count}건 변환")

            # COMPLETED -> completed
            updated = conn.execute(text("""
                UPDATE reservations
                SET status = 'completed'::reservationstatus
                WHERE status = 'COMPLETED'::reservationstatus
                RETURNING reservation_id
            """))
            count = len(updated.fetchall())
            print(f"   COMPLETED -> completed: {count}건 변환")

            # NO_SHOW -> no_show
            updated = conn.execute(text("""
                UPDATE reservations
                SET status = 'no_show'::reservationstatus
                WHERE status = 'NO_SHOW'::reservationstatus
                RETURNING reservation_id
            """))
            count = len(updated.fetchall())
            print(f"   NO_SHOW -> no_show: {count}건 변환")

            trans.commit()
            print("\n✅ 데이터 변환 완료!")

            # 2. 새로운 enum 타입 생성 (소문자만)
            print("\n2. 새로운 enum 타입 생성 (소문자만)...")
            trans = conn.begin()

            # 새 타입 생성
            conn.execute(text("DROP TYPE IF EXISTS reservationstatus_new CASCADE"))
            conn.execute(text("""
                CREATE TYPE reservationstatus_new AS ENUM (
                    'pending', 'confirmed', 'cancelled', 'completed', 'no_show'
                )
            """))

            # 컬럼 타입 변경
            conn.execute(text("""
                ALTER TABLE reservations
                ALTER COLUMN status TYPE reservationstatus_new
                USING status::text::reservationstatus_new
            """))

            # 기존 타입 삭제
            conn.execute(text("DROP TYPE reservationstatus"))

            # 새 타입 이름 변경
            conn.execute(text("ALTER TYPE reservationstatus_new RENAME TO reservationstatus"))

            trans.commit()
            print("✅ Enum 타입 정리 완료!")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ 오류 발생: {e}")
            raise

if __name__ == "__main__":
    # 1. 현재 상태 확인
    uppercase, lowercase = check_enums()

    # 2. 대문자 값이 있으면 정리
    if uppercase:
        print(f"\n⚠️  대문자 enum 값이 발견되었습니다: {uppercase}")
        response = input("\n대문자 값을 제거하고 소문자로 통일하시겠습니까? (y/n): ")

        if response.lower() == 'y':
            remove_uppercase_enums()

            # 결과 재확인
            print("\n=== 정리 후 상태 확인 ===")
            check_enums()
    else:
        print("\n✅ enum 값이 이미 소문자로 통일되어 있습니다.")
