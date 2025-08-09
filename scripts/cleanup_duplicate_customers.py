#!/usr/bin/env python3
"""
중복/테스트 고객 데이터 정리 스크립트
1. 삭제 대상 데이터 백업
2. 6/25 import 중복 데이터 삭제
3. 6/27 이후 테스트 데이터 삭제
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
import json

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/aibio_center.db")
if DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///.", "sqlite:////Users/vibetj/coding/center/backend")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def backup_data():
    """삭제 전 데이터 백업"""
    print("📦 데이터 백업 시작...")

    # 백업 디렉토리 생성
    backup_dir = "/Users/vibetj/coding/center/backup"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 전체 고객 데이터 백업
    all_customers_query = "SELECT * FROM customers"
    all_customers_df = pd.read_sql_query(all_customers_query, engine)
    backup_file = f"{backup_dir}/customers_backup_{timestamp}.csv"
    all_customers_df.to_csv(backup_file, index=False, encoding='utf-8-sig')
    print(f"  ✅ 전체 고객 백업 완료: {backup_file}")

    # 삭제 대상 데이터 식별
    # 1. 6/25 생성 데이터 (전화번호 없음)
    june25_query = """
    SELECT customer_id, name, created_at
    FROM customers
    WHERE DATE(created_at) = '2025-06-25'
    ORDER BY customer_id
    """
    june25_df = pd.read_sql_query(june25_query, engine)

    # 2. 6/27 이후 생성된 테스트 데이터 (전화번호, 이메일, 첫방문일 모두 없음)
    test_data_query = """
    SELECT customer_id, name, created_at
    FROM customers
    WHERE DATE(created_at) >= '2025-06-27'
    AND (phone IS NULL OR phone = '')
    AND (email IS NULL OR email = '')
    AND first_visit_date IS NULL
    ORDER BY customer_id
    """
    test_data_df = pd.read_sql_query(test_data_query, engine)

    # 삭제 대상 저장
    delete_info = {
        'timestamp': timestamp,
        'june25_count': len(june25_df),
        'june25_ids': june25_df['customer_id'].tolist(),
        'test_data_count': len(test_data_df),
        'test_data_ids': test_data_df['customer_id'].tolist(),
        'total_to_delete': len(june25_df) + len(test_data_df)
    }

    # 삭제 대상 정보 저장
    delete_info_file = f"{backup_dir}/delete_info_{timestamp}.json"
    with open(delete_info_file, 'w', encoding='utf-8') as f:
        json.dump(delete_info, f, ensure_ascii=False, indent=2)

    print(f"\n📊 삭제 대상 데이터:")
    print(f"  - 6/25 import 데이터: {len(june25_df)}명")
    print(f"  - 6/27 이후 테스트 데이터: {len(test_data_df)}명")
    print(f"  - 총 삭제 예정: {delete_info['total_to_delete']}명")

    return delete_info

def delete_duplicate_data(delete_info):
    """중복/테스트 데이터 삭제"""
    print("\n🗑️  데이터 삭제 시작...")

    try:
        # 트랜잭션 시작
        # 1. 6/25 데이터 삭제
        if delete_info['june25_ids']:
            june25_ids_str = ','.join(map(str, delete_info['june25_ids']))
            delete_june25 = f"DELETE FROM customers WHERE customer_id IN ({june25_ids_str})"
            result1 = session.execute(text(delete_june25))
            print(f"  ✅ 6/25 데이터 삭제: {result1.rowcount}명")

        # 2. 6/27 이후 테스트 데이터 삭제
        if delete_info['test_data_ids']:
            test_ids_str = ','.join(map(str, delete_info['test_data_ids']))
            delete_test = f"DELETE FROM customers WHERE customer_id IN ({test_ids_str})"
            result2 = session.execute(text(delete_test))
            print(f"  ✅ 테스트 데이터 삭제: {result2.rowcount}명")

        # 커밋
        session.commit()
        print("  ✅ 삭제 완료!")

    except Exception as e:
        session.rollback()
        print(f"  ❌ 삭제 실패: {e}")
        raise

def verify_cleanup():
    """정리 후 데이터 검증"""
    print("\n🔍 데이터 검증...")

    # 현재 고객 수
    total_count = session.execute(text("SELECT COUNT(*) FROM customers")).scalar()
    print(f"  현재 전체 고객 수: {total_count}명")

    # 원본 엑셀 데이터와 비교
    print(f"  원본 엑셀 고객 수: 950명")
    print(f"  차이: {total_count - 950}명")

    # 날짜별 분포
    date_dist_query = """
    SELECT DATE(created_at) as created_date, COUNT(*) as count
    FROM customers
    GROUP BY DATE(created_at)
    ORDER BY created_date
    """
    date_dist = pd.read_sql_query(date_dist_query, engine)

    print("\n📅 생성일별 고객 수:")
    for _, row in date_dist.iterrows():
        if row['count'] > 10:
            print(f"  {row['created_date']}: {row['count']}명")

    # 데이터 품질 확인
    quality_query = """
    SELECT
        COUNT(*) as total,
        COUNT(phone) as with_phone,
        COUNT(email) as with_email,
        COUNT(first_visit_date) as with_visit
    FROM customers
    """
    quality = pd.read_sql_query(quality_query, engine).iloc[0]

    print("\n📊 데이터 품질:")
    print(f"  전화번호 있음: {quality['with_phone']}/{quality['total']} ({quality['with_phone']/quality['total']*100:.1f}%)")
    print(f"  이메일 있음: {quality['with_email']}/{quality['total']} ({quality['with_email']/quality['total']*100:.1f}%)")
    print(f"  첫방문일 있음: {quality['with_visit']}/{quality['total']} ({quality['with_visit']/quality['total']*100:.1f}%)")

def main():
    print("🧹 고객 데이터 정리 시작")
    print("="*60)

    # 1. 백업
    delete_info = backup_data()

    # 2. 확인
    print("\n⚠️  정말로 삭제하시겠습니까?")
    print(f"삭제될 데이터: {delete_info['total_to_delete']}명")
    response = input("계속하려면 'yes'를 입력하세요: ")

    if response.lower() == 'yes':
        # 3. 삭제
        delete_duplicate_data(delete_info)

        # 4. 검증
        verify_cleanup()

        print("\n✅ 데이터 정리 완료!")
    else:
        print("\n❌ 취소되었습니다.")

    session.close()

if __name__ == "__main__":
    main()
