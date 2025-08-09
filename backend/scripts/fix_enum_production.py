#!/usr/bin/env python3
"""
프로덕션 환경의 enum 문제를 안전하게 해결하는 스크립트
"""

import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/aibio_center")
engine = create_engine(DATABASE_URL)

def check_and_fix_enums():
    """enum 상태 확인 후 필요시 수정"""

    with engine.connect() as conn:
        print("=== Enum 상태 확인 ===\n")

        # 1. ReservationStatus 확인
        try:
            result = conn.execute(text("""
                SELECT unnest(enum_range(NULL::reservationstatus)) AS enum_value
            """))
            reservation_values = [row[0] for row in result]
            print(f"ReservationStatus 현재 값: {reservation_values}")

            # 소문자 값이 없으면 추가
            lowercase_values = ['pending', 'confirmed', 'cancelled', 'completed', 'no_show']
            missing_values = [v for v in lowercase_values if v not in reservation_values]

            if missing_values:
                print(f"누락된 소문자 값 발견: {missing_values}")
                print("enum 값 추가 중...")

                # 트랜잭션 시작
                trans = conn.begin()
                try:
                    # 각 누락된 값 추가
                    for value in missing_values:
                        conn.execute(text(f"""
                            ALTER TYPE reservationstatus ADD VALUE IF NOT EXISTS '{value}'
                        """))
                    trans.commit()
                    print("✅ ReservationStatus enum 수정 완료")
                except Exception as e:
                    trans.rollback()
                    print(f"❌ 오류: {e}")
            else:
                print("✅ ReservationStatus enum은 이미 정상입니다")

        except Exception as e:
            print(f"ReservationStatus 확인 중 오류: {e}")

        print("\n=== 데이터 확인 ===")

        # 예약 데이터 상태 확인
        try:
            status_count = conn.execute(text("""
                SELECT status, COUNT(*) as count
                FROM reservations
                GROUP BY status
            """))

            print("\n예약 상태 분포:")
            for row in status_count:
                print(f"  - {row[0]}: {row[1]}건")

        except Exception as e:
            print(f"데이터 확인 중 오류: {e}")

if __name__ == "__main__":
    check_and_fix_enums()
