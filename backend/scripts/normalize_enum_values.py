#!/usr/bin/env python3
"""
모든 enum 값을 소문자로 통일하는 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings

engine = create_engine(settings.DATABASE_URL)

def normalize_enums():
    """모든 enum 값을 소문자로 통일"""

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("=== Enum 값 정규화 시작 ===\n")

            # 1. ReservationStatus enum 처리
            print("1. ReservationStatus enum 처리...")

            # 새 enum 타입 생성 (소문자만)
            conn.execute(text("DROP TYPE IF EXISTS reservationstatus_new CASCADE"))
            conn.execute(text("""
                CREATE TYPE reservationstatus_new AS ENUM (
                    'pending', 'confirmed', 'cancelled', 'completed', 'no_show'
                )
            """))

            # 데이터 변환 및 컬럼 타입 변경
            conn.execute(text("""
                ALTER TABLE reservations
                ALTER COLUMN status TYPE reservationstatus_new
                USING LOWER(status::text)::reservationstatus_new
            """))

            # 기존 타입 삭제 및 이름 변경
            conn.execute(text("DROP TYPE reservationstatus"))
            conn.execute(text("ALTER TYPE reservationstatus_new RENAME TO reservationstatus"))
            print("   ✓ ReservationStatus 완료")

            # 2. MembershipLevel enum 처리
            print("\n2. MembershipLevel enum 처리...")

            # 새 enum 타입 생성 (소문자만)
            conn.execute(text("DROP TYPE IF EXISTS membershiplevel_new CASCADE"))
            conn.execute(text("""
                CREATE TYPE membershiplevel_new AS ENUM (
                    'basic', 'silver', 'gold', 'platinum', 'vip'
                )
            """))

            # 데이터 변환 및 컬럼 타입 변경
            conn.execute(text("""
                ALTER TABLE customers
                ALTER COLUMN membership_level TYPE membershiplevel_new
                USING LOWER(membership_level::text)::membershiplevel_new
            """))

            # 기존 타입 삭제 및 이름 변경
            conn.execute(text("DROP TYPE membershiplevel"))
            conn.execute(text("ALTER TYPE membershiplevel_new RENAME TO membershiplevel"))
            print("   ✓ MembershipLevel 완료")

            # 3. CustomerStatus enum 처리
            print("\n3. CustomerStatus enum 처리...")

            # 새 enum 타입 생성 (소문자만)
            conn.execute(text("DROP TYPE IF EXISTS customerstatus_new CASCADE"))
            conn.execute(text("""
                CREATE TYPE customerstatus_new AS ENUM (
                    'active', 'inactive', 'dormant'
                )
            """))

            # 데이터 변환 및 컬럼 타입 변경
            conn.execute(text("""
                ALTER TABLE customers
                ALTER COLUMN status TYPE customerstatus_new
                USING LOWER(status::text)::customerstatus_new
            """))

            # 기존 타입 삭제 및 이름 변경
            conn.execute(text("DROP TYPE customerstatus"))
            conn.execute(text("ALTER TYPE customerstatus_new RENAME TO customerstatus"))
            print("   ✓ CustomerStatus 완료")

            # 4. PaymentStatus enum 처리
            print("\n4. PaymentStatus enum 처리...")

            # 새 enum 타입 생성 (소문자만)
            conn.execute(text("DROP TYPE IF EXISTS paymentstatus_new CASCADE"))
            conn.execute(text("""
                CREATE TYPE paymentstatus_new AS ENUM (
                    'pending', 'paid', 'cancelled', 'refunded', 'partial_refund'
                )
            """))

            # 데이터 변환 및 컬럼 타입 변경
            conn.execute(text("""
                ALTER TABLE payments
                ALTER COLUMN payment_status TYPE paymentstatus_new
                USING LOWER(payment_status::text)::paymentstatus_new
            """))

            # 기존 타입 삭제 및 이름 변경
            conn.execute(text("DROP TYPE paymentstatus"))
            conn.execute(text("ALTER TYPE paymentstatus_new RENAME TO paymentstatus"))
            print("   ✓ PaymentStatus 완료")

            trans.commit()
            print("\n✅ 모든 enum 값이 소문자로 정규화되었습니다!")

            # 결과 확인
            print("\n=== 정규화 결과 확인 ===")

            # 각 enum 타입의 값 확인
            enums = ['reservationstatus', 'membershiplevel', 'customerstatus', 'paymentstatus']
            for enum in enums:
                result = conn.execute(text(f"""
                    SELECT unnest(enum_range(NULL::{enum})) AS enum_value
                """))
                values = [row[0] for row in result]
                print(f"\n{enum}: {values}")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ 오류 발생: {e}")
            raise

if __name__ == "__main__":
    normalize_enums()
