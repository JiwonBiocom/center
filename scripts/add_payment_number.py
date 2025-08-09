#!/usr/bin/env python3
"""
결제 테이블에 payment_number 컬럼 추가 및 기존 데이터에 번호 할당
"""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

# 환경 변수 로드
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

def add_payment_number_column():
    """payment_number 컬럼 추가 및 데이터 업데이트"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # 트랜잭션 시작
        trans = conn.begin()
        try:
            # 1. 컬럼이 이미 존재하는지 확인
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'payments'
                AND column_name = 'payment_number'
            """)).fetchone()

            if result:
                print("✅ payment_number 컬럼이 이미 존재합니다.")
            else:
                # 2. payment_number 컬럼 추가
                print("📌 payment_number 컬럼 추가 중...")
                conn.execute(text("""
                    ALTER TABLE payments
                    ADD COLUMN payment_number VARCHAR(20)
                """))
                print("✅ payment_number 컬럼 추가 완료")

            # 3. 기존 데이터에 결제번호 할당
            print("\n📌 기존 결제 데이터에 번호 할당 중...")

            # payment_number가 NULL인 결제 찾기
            null_payments = conn.execute(text("""
                SELECT payment_id, payment_date
                FROM payments
                WHERE payment_number IS NULL
                ORDER BY payment_date, payment_id
            """)).fetchall()

            if null_payments:
                print(f"   - 번호 할당이 필요한 결제: {len(null_payments)}건")

                # 각 결제에 번호 할당
                for idx, payment in enumerate(null_payments, 1):
                    payment_number = f"PAY-{payment.payment_date.year}-{idx:06d}"
                    conn.execute(text("""
                        UPDATE payments
                        SET payment_number = :payment_number
                        WHERE payment_id = :payment_id
                    """), {"payment_number": payment_number, "payment_id": payment.payment_id})

                    if idx % 100 == 0:
                        print(f"   - {idx}건 처리 완료...")

                print(f"✅ {len(null_payments)}건의 결제에 번호 할당 완료")
            else:
                print("✅ 모든 결제에 이미 번호가 할당되어 있습니다.")

            # 4. UNIQUE 인덱스 생성 (없는 경우만)
            try:
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_number
                    ON payments(payment_number)
                """))
                print("✅ payment_number UNIQUE 인덱스 생성 완료")
            except Exception as e:
                print(f"ℹ️  인덱스는 이미 존재하거나 생성할 수 없습니다: {e}")

            # 커밋
            trans.commit()
            print("\n✅ 모든 작업이 성공적으로 완료되었습니다!")

            # 5. 결과 확인
            result = conn.execute(text("""
                SELECT
                    COUNT(*) as total_payments,
                    COUNT(payment_number) as with_number,
                    MIN(payment_number) as first_number,
                    MAX(payment_number) as last_number
                FROM payments
            """)).fetchone()

            print(f"\n📊 결과:")
            print(f"   - 전체 결제: {result.total_payments}건")
            print(f"   - 번호 할당: {result.with_number}건")
            print(f"   - 첫 번호: {result.first_number}")
            print(f"   - 마지막 번호: {result.last_number}")

        except Exception as e:
            trans.rollback()
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_payment_number_column()
