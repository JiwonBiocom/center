import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine

def verify_migration():
    """마이그레이션 데이터 검증"""

    load_dotenv()

    with engine.connect() as conn:
        print("=== 데이터베이스 현황 ===\n")

        # 1. 고객 수
        result = conn.execute(text("SELECT COUNT(*) FROM customers"))
        customer_count = result.scalar()
        print(f"전체 고객 수: {customer_count}명")

        # 2. 패키지 구매 현황
        result = conn.execute(text("""
            SELECT p.package_name, COUNT(*) as purchase_count,
                   SUM(pp.total_sessions) as total_sessions,
                   SUM(pp.used_sessions) as used_sessions,
                   SUM(pp.remaining_sessions) as remaining_sessions
            FROM package_purchases pp
            JOIN packages p ON pp.package_id = p.package_id
            GROUP BY p.package_name
            ORDER BY purchase_count DESC
        """))

        print("\n패키지별 구매 현황:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}건 구매")
            print(f"    전체 {row[2]}회, 사용 {row[3]}회, 잔여 {row[4]}회")

        # 3. 서비스 이용 현황
        result = conn.execute(text("""
            SELECT st.service_name, COUNT(*) as usage_count
            FROM service_usage su
            JOIN service_types st ON su.service_type_id = st.service_type_id
            GROUP BY st.service_name
            ORDER BY usage_count DESC
        """))

        print("\n서비스별 이용 현황:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}회")

        # 4. 상위 이용 고객
        result = conn.execute(text("""
            SELECT c.name, COUNT(*) as service_count
            FROM service_usage su
            JOIN customers c ON su.customer_id = c.customer_id
            GROUP BY c.customer_id, c.name
            ORDER BY service_count DESC
            LIMIT 10
        """))

        print("\n서비스 이용 상위 10명:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}회")

        # 5. 월별 서비스 이용 추이
        result = conn.execute(text("""
            SELECT DATE_TRUNC('month', service_date) as month,
                   COUNT(*) as service_count
            FROM service_usage
            WHERE service_date >= '2024-01-01'
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """))

        print("\n최근 12개월 서비스 이용 추이:")
        for row in result:
            print(f"  - {row[0].strftime('%Y-%m')}: {row[1]}회")

        # 6. 패키지 없는 고객
        result = conn.execute(text("""
            SELECT COUNT(DISTINCT c.customer_id)
            FROM customers c
            LEFT JOIN package_purchases pp ON c.customer_id = pp.customer_id
            WHERE pp.purchase_id IS NULL
        """))
        no_package_count = result.scalar()
        print(f"\n패키지 구매 없는 고객: {no_package_count}명")

        # 7. 서비스 이용 없는 고객
        result = conn.execute(text("""
            SELECT COUNT(DISTINCT c.customer_id)
            FROM customers c
            LEFT JOIN service_usage su ON c.customer_id = su.customer_id
            WHERE su.usage_id IS NULL
        """))
        no_service_count = result.scalar()
        print(f"서비스 이용 없는 고객: {no_service_count}명")

if __name__ == "__main__":
    print("마이그레이션 데이터 검증 시작...\n")
    verify_migration()
    print("\n검증 완료!")
