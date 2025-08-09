#!/usr/bin/env python3
"""
프로덕션 환경 enum 자동 수정 스크립트
사용자 입력 없이 자동으로 실행
"""

import os
from sqlalchemy import create_engine, text
import sys

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

def fix_all_enums():
    """모든 enum을 소문자로 통일"""

    with engine.connect() as conn:
        print("=== Enum 자동 수정 시작 ===\n")

        # 1. 현재 상태 확인
        print("1. 현재 enum 상태 확인...")
        try:
            result = conn.execute(text("""
                SELECT unnest(enum_range(NULL::reservationstatus)) AS enum_value
            """))
            current_values = [row[0] for row in result]
            print(f"   현재 값: {current_values}")

            # 대문자가 있는지 확인
            has_uppercase = any(v.isupper() for v in current_values)

            if not has_uppercase:
                print("✅ 이미 모든 enum이 소문자입니다.")
                return

        except Exception as e:
            print(f"enum 확인 중 오류: {e}")
            return

        # 2. 데이터 변환
        trans = conn.begin()
        try:
            print("\n2. 대문자 데이터를 소문자로 변환...")

            conversions = [
                ('PENDING', 'pending'),
                ('CONFIRMED', 'confirmed'),
                ('CANCELLED', 'cancelled'),
                ('COMPLETED', 'completed'),
                ('NO_SHOW', 'no_show')
            ]

            for old_val, new_val in conversions:
                if old_val in current_values:
                    result = conn.execute(text(f"""
                        UPDATE reservations
                        SET status = '{new_val}'::reservationstatus
                        WHERE status = '{old_val}'::reservationstatus
                    """))
                    print(f"   {old_val} -> {new_val}: {result.rowcount}건")

            trans.commit()
            print("✅ 데이터 변환 완료")

        except Exception as e:
            trans.rollback()
            print(f"❌ 데이터 변환 중 오류: {e}")
            return

        # 3. Enum 타입 재생성
        trans = conn.begin()
        try:
            print("\n3. Enum 타입을 소문자만으로 재생성...")

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

            # 기타 테이블도 확인 (staff_schedule 등)
            try:
                conn.execute(text("""
                    ALTER TABLE staff_schedule
                    ALTER COLUMN status TYPE reservationstatus_new
                    USING status::text::reservationstatus_new
                """))
            except:
                pass  # staff_schedule이 없거나 status 컬럼이 없을 수 있음

            # 기존 타입 삭제 및 이름 변경
            conn.execute(text("DROP TYPE reservationstatus"))
            conn.execute(text("ALTER TYPE reservationstatus_new RENAME TO reservationstatus"))

            trans.commit()
            print("✅ Enum 타입 재생성 완료")

        except Exception as e:
            trans.rollback()
            print(f"❌ Enum 타입 재생성 중 오류: {e}")
            return

        # 4. 최종 확인
        print("\n4. 최종 상태 확인...")
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::reservationstatus)) AS enum_value
        """))
        final_values = [row[0] for row in result]
        print(f"   최종 enum 값: {final_values}")

        # 데이터 분포 확인
        status_dist = conn.execute(text("""
            SELECT status, COUNT(*) as count
            FROM reservations
            GROUP BY status
        """))

        print("\n   예약 상태 분포:")
        for row in status_dist:
            print(f"   - {row[0]}: {row[1]}건")

        print("\n✅ 모든 작업 완료!")

if __name__ == "__main__":
    fix_all_enums()
