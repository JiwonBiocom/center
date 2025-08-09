#!/usr/bin/env python3
"""
예약 상태 enum 문제 해결 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings

engine = create_engine(settings.DATABASE_URL)

def fix_reservation_status():
    """예약 상태 enum 문제 해결"""

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("=== 예약 상태 Enum 수정 ===\n")

            # 1. 현재 enum 타입 확인
            print("1. 현재 enum 타입 확인...")
            enum_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'reservationstatus'
                )
            """)).scalar()

            if enum_exists:
                # 기존 enum 값 확인
                result = conn.execute(text("""
                    SELECT unnest(enum_range(NULL::reservationstatus)) AS enum_value
                """))
                enum_values = [row[0] for row in result]
                print(f"   현재 enum 값: {enum_values}")

                # 소문자 값이 있는지 확인
                has_lowercase = any(v.islower() for v in enum_values)
                has_uppercase = any(v.isupper() for v in enum_values)

                if has_uppercase and not has_lowercase:
                    print("   대문자 enum만 있음. 소문자 값 추가 필요")

                    # 새로운 enum 타입 생성
                    print("\n2. 새 enum 타입 생성...")
                    conn.execute(text("""
                        CREATE TYPE reservationstatus_new AS ENUM (
                            'pending', 'confirmed', 'cancelled', 'completed', 'no_show',
                            'PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW'
                        )
                    """))

                    # 컬럼 타입 변경
                    print("3. 컬럼 타입 변경...")
                    conn.execute(text("""
                        ALTER TABLE reservations
                        ALTER COLUMN status TYPE reservationstatus_new
                        USING status::text::reservationstatus_new
                    """))

                    # 기존 enum 삭제
                    print("4. 기존 enum 삭제...")
                    conn.execute(text("DROP TYPE reservationstatus"))

                    # 새 enum 이름 변경
                    print("5. enum 이름 변경...")
                    conn.execute(text("ALTER TYPE reservationstatus_new RENAME TO reservationstatus"))

                    print("\n✅ enum 타입 수정 완료!")
                else:
                    print("   이미 소문자 값이 포함되어 있음")

            trans.commit()

        except Exception as e:
            trans.rollback()
            print(f"\n❌ 오류 발생: {e}")
            raise

if __name__ == "__main__":
    fix_reservation_status()
