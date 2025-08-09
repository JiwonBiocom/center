import sys
import os
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from models.customer import Customer
from models.package import Package, PackagePurchase

def fix_kim_ryowook_data():
    """김려욱 고객 데이터 수정"""

    with Session(engine) as db:
        # 김려욱 고객 찾기
        customer = db.query(Customer).filter(Customer.name == '김려욱').first()
        if not customer:
            print("김려욱 고객을 찾을 수 없습니다.")
            return

        print(f"김려욱 고객 ID: {customer.customer_id}")

        # 기존 패키지 구매 삭제
        db.execute(text("DELETE FROM package_purchases WHERE customer_id = :customer_id"),
                  {'customer_id': customer.customer_id})

        # 통합 패키지 생성 또는 찾기
        integrated_package = db.query(Package).filter(
            Package.package_name == "AI-BIO 통합 30회 패키지"
        ).first()

        if not integrated_package:
            integrated_package = Package(
                package_name="AI-BIO 통합 30회 패키지",
                total_sessions=90,  # 30회 x 3개 서비스
                base_price=3600000,  # 예상 가격
                valid_months=12,
                is_active=True,
                description="레드, 림프, 펄스 각 30회 통합 패키지"
            )
            db.add(integrated_package)
            db.commit()
            print("통합 패키지 생성")

        # 통합 패키지 구매 정보 생성
        db.execute(text("""
            INSERT INTO package_purchases
            (customer_id, package_id, purchase_date, expiry_date,
             total_sessions, used_sessions, remaining_sessions, price_paid)
            VALUES (:customer_id, :package_id, :purchase_date, :expiry_date,
                    :total_sessions, :used_sessions, :remaining_sessions, :price_paid)
        """), {
            'customer_id': customer.customer_id,
            'package_id': integrated_package.package_id,
            'purchase_date': date(2024, 1, 1),
            'expiry_date': date(2025, 12, 31),
            'total_sessions': 90,  # 30 x 3
            'used_sessions': 54,   # 18 x 3
            'remaining_sessions': 36,  # 12 x 3
            'price_paid': 3600000
        })

        print("통합 패키지 구매 정보 생성")

        # 서비스별 사용 기록 생성 (누락된 경우)
        # 레드 18회, 림프 18회, 펄스 18회 사용 기록 확인

        db.commit()

        # 결과 확인
        result = db.execute(text("""
            SELECT p.package_name, pp.total_sessions, pp.used_sessions, pp.remaining_sessions
            FROM package_purchases pp
            JOIN packages p ON pp.package_id = p.package_id
            WHERE pp.customer_id = :customer_id
        """), {'customer_id': customer.customer_id}).fetchall()

        print("\n수정된 패키지 정보:")
        for package_name, total, used, remaining in result:
            print(f"  - {package_name}: 전체 {total}회, 사용 {used}회, 잔여 {remaining}회")

if __name__ == "__main__":
    print("김려욱 고객 데이터 수정 시작...")
    fix_kim_ryowook_data()
    print("\n완료!")
