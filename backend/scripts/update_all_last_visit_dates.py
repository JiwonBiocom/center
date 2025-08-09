from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    print("모든 고객의 last_visit_date 업데이트 시작...")

    # 실제 마지막 서비스 이용일과 다른 고객 찾기
    result = conn.execute(text('''
        SELECT c.customer_id, c.name, c.last_visit_date,
               MAX(su.service_date) as actual_last_visit,
               c.membership_level
        FROM customers c
        LEFT JOIN service_usage su ON c.customer_id = su.customer_id
        GROUP BY c.customer_id, c.name, c.last_visit_date, c.membership_level
        HAVING MAX(su.service_date) != c.last_visit_date
           AND MAX(su.service_date) IS NOT NULL
    '''))

    customers_to_update = result.fetchall()
    print(f"\n업데이트가 필요한 고객: {len(customers_to_update)}명")

    updated_count = 0
    for customer in customers_to_update:
        customer_id, name, db_last_visit, actual_last_visit, current_level = customer

        # 경과일 계산
        today = datetime.now().date()
        days_since_visit = (today - actual_last_visit).days

        # 새로운 멤버십 레벨 결정
        if days_since_visit < 30:
            new_level = 'vip'
        elif days_since_visit < 60:
            new_level = 'gold'
        elif days_since_visit < 90:
            new_level = 'silver'
        else:
            new_level = 'basic'  # 90일 이상은 모두 basic

        # 업데이트
        conn.execute(text('''
            UPDATE customers
            SET last_visit_date = :actual_last_visit,
                membership_level = :new_level
            WHERE customer_id = :customer_id
        '''), {
            'actual_last_visit': actual_last_visit,
            'new_level': new_level,
            'customer_id': customer_id
        })

        updated_count += 1
        if updated_count <= 10:  # 처음 10명만 출력
            print(f"  - {name}: {db_last_visit} → {actual_last_visit} (레벨: {current_level} → {new_level})")

    conn.commit()

    if updated_count > 10:
        print(f"  ... 외 {updated_count - 10}명")

    print(f"\n총 {updated_count}명의 고객 정보가 업데이트되었습니다.")

    # 멤버십 레벨별 통계
    result = conn.execute(text('''
        SELECT membership_level, COUNT(*)
        FROM customers
        GROUP BY membership_level
        ORDER BY
            CASE membership_level
                WHEN 'vip' THEN 1
                WHEN 'gold' THEN 2
                WHEN 'silver' THEN 3
                WHEN 'basic' THEN 4
                WHEN 'platinum' THEN 5
                ELSE 6
            END
    '''))

    print("\n업데이트 후 멤버십 레벨 분포:")
    for level, count in result:
        print(f"  - {level}: {count}명")
