from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # 김려욱 고객 현재 상태
    result = conn.execute(text('''
        SELECT c.customer_id, c.name, c.membership_level, c.last_visit_date,
               MAX(su.service_date) as last_service_date
        FROM customers c
        LEFT JOIN service_usage su ON c.customer_id = su.customer_id
        WHERE c.name = '김려욱'
        GROUP BY c.customer_id, c.name, c.membership_level, c.last_visit_date
    '''))

    customer = result.fetchone()
    if customer:
        today = datetime.now().date()
        last_service = customer[4]
        days_since = (today - last_service).days if last_service else 999

        print(f'고객: {customer[1]}')
        print(f'현재 멤버십 레벨: {customer[2]}')
        print(f'DB의 last_visit_date: {customer[3]}')
        print(f'실제 마지막 서비스: {customer[4]}')
        print(f'마지막 방문 후 경과일: {days_since}일')
        print(f'')
        print(f'=> 28일 경과이므로 "vip" 레벨이어야 함 (30일 미만)')

        if customer[3] != customer[4]:
            # 업데이트 필요
            conn.execute(text('''
                UPDATE customers
                SET last_visit_date = :last_service,
                    membership_level = 'vip'
                WHERE customer_id = :customer_id
            '''), {
                'last_service': last_service,
                'customer_id': customer[0]
            })
            conn.commit()
            print(f'\n=> 업데이트 완료: last_visit_date를 {last_service}로, 레벨을 vip로 변경')
