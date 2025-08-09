#!/usr/bin/env python3
"""
2025년 5월 결제 데이터 정정 스크립트
엑셀 파일의 실제 데이터와 맞추기
"""

import pandas as pd
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.database import get_db
from models.payment import Payment as PaymentModel
from models.customer import Customer as CustomerModel
from datetime import datetime

def fix_may_2025_payment_data():
    """2025년 5월 결제 데이터를 엑셀 파일과 맞추기"""

    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        print("🔧 2025년 5월 결제 데이터 정정 시작...")

        # 1. 기존 2025년 5월 데이터 삭제
        result = db.execute(text("""
            DELETE FROM payments
            WHERE payment_date BETWEEN '2025-05-01' AND '2025-05-31'
        """))
        deleted_count = result.rowcount
        print(f"📋 기존 5월 데이터 {deleted_count}건 삭제")

        # 2. 엑셀 파일에서 정확한 데이터 읽기
        excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx'

        # 2025년 5월 시트 읽기
        df = pd.read_excel(excel_path, sheet_name='2025년 5월', header=2)
        print(f"📊 엑셀에서 {len(df)}행 데이터 읽기 완료")
        print(f"📊 컬럼: {df.columns.tolist()}")

        success_count = 0
        skip_count = 0

        # 3. 데이터 처리
        for idx, row in df.iterrows():
            try:
                # 필수 데이터 체크
                if pd.isna(row.get('고객명')) or pd.isna(row.get('결제일자')):
                    skip_count += 1
                    continue

                customer_name = str(row.get('고객명', '')).strip()
                if not customer_name:
                    skip_count += 1
                    continue

                # 결제일자 파싱
                payment_date = row.get('결제일자')
                if pd.isna(payment_date):
                    skip_count += 1
                    continue

                if hasattr(payment_date, 'date'):
                    payment_date = payment_date.date()
                else:
                    skip_count += 1
                    continue

                # 결제금액 파싱
                amount = row.get('결제금액')
                if pd.isna(amount) or amount <= 0:
                    skip_count += 1
                    continue

                # 고객 찾기 (이름으로)
                customer = db.execute(
                    select(CustomerModel).where(CustomerModel.name == customer_name)
                ).scalar_one_or_none()

                if not customer:
                    print(f"⚠️  고객 '{customer_name}' 찾을 수 없음")
                    skip_count += 1
                    continue

                # 담당자 정보
                payment_staff = str(row.get('담당자', '')).strip()
                if payment_staff == 'nan':
                    payment_staff = ''

                # 승인번호로 결제방법 판단
                approval_number = str(row.get('승인번호', '')).strip()
                if approval_number in ['계좌이체', '무통장입금']:
                    payment_method = 'transfer'
                elif approval_number == '현금':
                    payment_method = 'cash'
                elif approval_number == '제로페이':
                    payment_method = 'other'
                else:
                    payment_method = 'card'

                if approval_number in ['nan', '계좌이체']:
                    approval_number = ''

                # 결제 생성
                payment = PaymentModel(
                    customer_id=customer.customer_id,
                    payment_date=payment_date,
                    amount=float(amount),
                    payment_method=payment_method,
                    payment_type='single',
                    payment_status='completed',
                    payment_staff=payment_staff,
                    transaction_id=approval_number,
                    card_holder_name=str(row.get('카드명의자', '')).strip(),
                    reference_type=str(row.get('결제프로그램명', '')).strip(),
                    notes=f"2025년 5월 실제 데이터 (엑셀 기준)"
                )

                db.add(payment)
                success_count += 1

            except Exception as e:
                print(f"❌ 행 {idx + 1} 처리 오류: {e}")
                skip_count += 1

        # 커밋
        db.commit()

        print(f"✅ 처리 완료!")
        print(f"  - 성공: {success_count}건")
        print(f"  - 건너뜀: {skip_count}건")

        # 결과 확인
        result = db.execute(text("""
            SELECT payment_staff, COUNT(*) as count
            FROM payments
            WHERE payment_date BETWEEN '2025-05-01' AND '2025-05-31'
            GROUP BY payment_staff
            ORDER BY count DESC
        """))

        print("\\n📊 정정된 2025년 5월 담당자 통계:")
        for row in result:
            print(f"  - {row[0] or '(담당자 없음)'}: {row[1]}건")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_may_2025_payment_data()
