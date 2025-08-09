from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    print("모든 고객의 customer_status 업데이트 시작...")

    # 모든 고객의 상태 업데이트
    result = conn.execute(text('''
        UPDATE customers
        SET customer_status = CASE
            WHEN last_visit_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'active'::customer_status
            WHEN last_visit_date >= CURRENT_DATE - INTERVAL '90 days' THEN 'inactive'::customer_status
            ELSE 'dormant'::customer_status
        END
        WHERE last_visit_date IS NOT NULL
    '''))

    updated_count = result.rowcount
    conn.commit()

    print(f"{updated_count}명의 고객 상태가 업데이트되었습니다.")

    # 상태별 고객 수 확인
    result = conn.execute(text('''
        SELECT customer_status, COUNT(*) as count
        FROM customers
        GROUP BY customer_status
        ORDER BY customer_status
    '''))

    print("\n고객 상태별 분포:")
    for status, count in result:
        print(f"  - {status}: {count}명")

    # 김려욱 고객 확인
    result = conn.execute(text('''
        SELECT name, membership_level, customer_status, last_visit_date
        FROM customers
        WHERE name = '김려욱'
    '''))

    customer = result.fetchone()
    if customer:
        print(f"\n김려욱 고객 현재 상태:")
        print(f"  - 멤버십 레벨: {customer[1]}")
        print(f"  - 고객 상태: {customer[2]}")
        print(f"  - 마지막 방문: {customer[3]}")

        days_since = (datetime.now().date() - customer[3]).days
        print(f"  - 경과일: {days_since}일")
