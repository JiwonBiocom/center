from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # 김려욱 고객 정보와 멤버십 레벨 확인
    result = conn.execute(text('''
        SELECT c.customer_id, c.name, c.membership_level, c.last_visit_date,
               MAX(su.service_date) as last_service_date,
               COUNT(su.usage_id) as total_services
        FROM customers c
        LEFT JOIN service_usage su ON c.customer_id = su.customer_id
        WHERE c.name = '김려욱'
        GROUP BY c.customer_id, c.name, c.membership_level, c.last_visit_date
    '''))

    customer = result.fetchone()
    if customer:
        print(f'고객 ID: {customer[0]}')
        print(f'이름: {customer[1]}')
        print(f'멤버십 레벨: {customer[2]}')
        print(f'마지막 방문일(DB): {customer[3]}')
        print(f'마지막 서비스 이용일: {customer[4]}')
        print(f'총 서비스 이용 횟수: {customer[5]}')

        # 현재 날짜와 비교
        today = datetime.now().date()
        last_service = customer[4]

        if last_service:
            days_since_visit = (today - last_service).days
            print(f'\n마지막 방문 후 경과일: {days_since_visit}일')
            print(f'휴면 기준 (90일): {"휴면" if days_since_visit > 90 else "활성"}')

        # last_visit_date 업데이트 필요 여부 확인
        if customer[3] != customer[4]:
            print(f'\n주의: last_visit_date({customer[3]})와 실제 마지막 서비스 날짜({customer[4]})가 다릅니다!')

        # 멤버십 레벨이 dormant인지 확인
        print(f'\n현재 멤버십 레벨: {customer[2]}')
        if customer[2] == 'dormant':
            print('=> 휴면 상태로 설정되어 있습니다.')

            # last_visit_date 업데이트
            conn.execute(text('''
                UPDATE customers
                SET last_visit_date = :last_service_date,
                    membership_level = CASE
                        WHEN :days_since < 30 THEN 'vip'
                        WHEN :days_since < 60 THEN 'gold'
                        WHEN :days_since < 90 THEN 'silver'
                        ELSE 'basic'
                    END
                WHERE customer_id = :customer_id
            '''), {
                'last_service_date': last_service,
                'days_since': days_since_visit,
                'customer_id': customer[0]
            })
            conn.commit()
            print(f'=> last_visit_date를 {last_service}로 업데이트하고 멤버십 레벨을 조정했습니다.')

        # 최근 서비스 이용 내역
        print('\n최근 서비스 이용 내역:')
        result = conn.execute(text('''
            SELECT service_date, session_details
            FROM service_usage
            WHERE customer_id = :customer_id
            ORDER BY service_date DESC
            LIMIT 5
        '''), {'customer_id': customer[0]})

        for row in result:
            print(f'  - {row[0]}: {row[1]}')
