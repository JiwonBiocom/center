#!/usr/bin/env python3

import sys
sys.path.append('.')
from core.database import get_db
from sqlalchemy import text

def restore_staff_data():
    db = next(get_db())

    print('🔍 백업 테이블에서 담당자 데이터 확인...')

    # 백업 테이블 확인
    sample = db.execute(text("""
        SELECT payment_id, payment_staff
        FROM payments_staff_backup
        WHERE payment_staff <> '직원'
        LIMIT 10
    """)).fetchall()

    print(f'실제 담당자 데이터 샘플 ({len(sample)}개):')
    for row in sample:
        print(f'  ID: {row[0]}, 담당자: {row[1]}')

    print('\n📊 백업의 담당자 통계:')
    backup_stats = db.execute(text("""
        SELECT payment_staff, COUNT(*)
        FROM payments_staff_backup
        GROUP BY payment_staff
        ORDER BY COUNT(*) DESC
    """)).fetchall()

    for staff, count in backup_stats:
        print(f'  {staff}: {count}건')

    print('\n🔄 담당자 데이터 복구 실행...')

    # 백업에서 복구 (직원이 아닌 실제 담당자만)
    result = db.execute(text("""
        UPDATE payments
        SET payment_staff = psb.payment_staff
        FROM payments_staff_backup psb
        WHERE payments.payment_id = psb.payment_id
        AND psb.payment_staff <> '직원'
    """))

    db.commit()
    print(f'✅ {result.rowcount}건의 담당자 데이터 복구 완료!')

    print('\n📊 복구 후 담당자 통계:')
    current_stats = db.execute(text("""
        SELECT payment_staff, COUNT(*)
        FROM payments
        GROUP BY payment_staff
        ORDER BY COUNT(*) DESC
    """)).fetchall()

    for staff, count in current_stats:
        print(f'  {staff}: {count}건')

if __name__ == "__main__":
    restore_staff_data()
