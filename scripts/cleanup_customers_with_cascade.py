#!/usr/bin/env python3
"""
관련 데이터를 포함한 고객 데이터 완전 삭제
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/aibio_center")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def delete_customers_with_cascade():
    """6/25 import 고객 데이터와 관련 데이터 삭제"""
    print("🗑️  6/25 import 데이터 삭제 시작...")

    # 6/25 생성 고객 ID 목록
    june25_ids = [
        1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109,
        1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120,
        1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130,
        1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140,
        1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1151, 1156,
        1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167,
        1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177,
        1178, 1181, 1182, 1183, 1184, 1185
    ]

    deleted_count = {
        'service_usage': 0,
        'payments': 0,
        'reservations': 0,
        'kit_receipts': 0,
        'customers': 0
    }

    try:
        # 트랜잭션 시작
        for customer_id in june25_ids:
            # 1. service_usage 삭제
            result = session.execute(
                text("DELETE FROM service_usage WHERE customer_id = :id"),
                {"id": customer_id}
            )
            deleted_count['service_usage'] += result.rowcount

            # 2. payments 삭제
            result = session.execute(
                text("DELETE FROM payments WHERE customer_id = :id"),
                {"id": customer_id}
            )
            deleted_count['payments'] += result.rowcount

            # 3. reservations 삭제
            result = session.execute(
                text("DELETE FROM reservations WHERE customer_id = :id"),
                {"id": customer_id}
            )
            deleted_count['reservations'] += result.rowcount

            # 4. kit_receipts 삭제
            result = session.execute(
                text("DELETE FROM kit_receipts WHERE customer_id = :id"),
                {"id": customer_id}
            )
            deleted_count['kit_receipts'] += result.rowcount

            # 5. 마지막으로 customer 삭제
            result = session.execute(
                text("DELETE FROM customers WHERE customer_id = :id"),
                {"id": customer_id}
            )
            if result.rowcount > 0:
                deleted_count['customers'] += 1
                print(f"  ✅ 고객 ID {customer_id} 삭제 완료")

        # 커밋
        session.commit()

        print("\n📊 삭제 결과:")
        print(f"  - 서비스 이용: {deleted_count['service_usage']}건")
        print(f"  - 결제 내역: {deleted_count['payments']}건")
        print(f"  - 예약: {deleted_count['reservations']}건")
        print(f"  - 키트 수령: {deleted_count['kit_receipts']}건")
        print(f"  - 고객: {deleted_count['customers']}명")

    except Exception as e:
        session.rollback()
        print(f"❌ 삭제 실패: {e}")
        raise
    finally:
        session.close()

def verify_final_count():
    """최종 고객 수 확인"""
    print("\n🔍 최종 데이터 확인...")

    # 전체 고객 수
    result = session.execute(text("SELECT COUNT(*) FROM customers"))
    total_count = result.scalar()

    print(f"  현재 전체 고객 수: {total_count}명")
    print(f"  원본 엑셀 고객 수: 950명")
    print(f"  차이: {total_count - 950}명")

    # 날짜별 분포
    date_query = """
    SELECT DATE(created_at) as date, COUNT(*) as count
    FROM customers
    GROUP BY DATE(created_at)
    HAVING COUNT(*) > 10
    ORDER BY date
    """
    result = session.execute(text(date_query))

    print("\n📅 생성일별 고객 수:")
    for row in result:
        print(f"  {row.date}: {row.count}명")

    session.close()

def main():
    print("🧹 6/25 import 데이터 완전 삭제")
    print("="*60)

    response = input("정말로 삭제하시겠습니까? (yes/no): ")
    if response.lower() == 'yes':
        delete_customers_with_cascade()
        verify_final_count()
        print("\n✅ 데이터 정리 완료!")
    else:
        print("❌ 취소되었습니다.")

if __name__ == "__main__":
    main()
