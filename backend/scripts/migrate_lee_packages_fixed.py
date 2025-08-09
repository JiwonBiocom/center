import pandas as pd
import sys
import os
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from models.customer import Customer
from models.package import Package, PackagePurchase

def create_lee_packages():
    """이성윤 고객의 정확한 패키지 정보 생성"""

    with Session(engine) as db:
        # 이성윤 고객 찾기
        customer = db.query(Customer).filter(Customer.name == '이성윤').first()
        if not customer:
            print("이성윤 고객을 찾을 수 없습니다.")
            return

        print(f"이성윤 고객 ID: {customer.customer_id}")

        # 기존 패키지 구매 삭제
        db.execute(text("DELETE FROM package_purchases WHERE customer_id = :customer_id"),
                  {'customer_id': customer.customer_id})

        # 펄스 패키지
        pulse_package = db.query(Package).filter(Package.package_name.like('%펄스%')).first()
        if not pulse_package:
            pulse_package = Package(
                package_name="펄스 24회 패키지",
                total_sessions=24,
                base_price=960000,  # 40,000원 * 24회
                valid_months=12,
                is_active=True,
                description="고주파 전신 관리 패키지"
            )
            db.add(pulse_package)
            db.commit()
            print("펄스 패키지 생성")

        # 펄스 패키지 구매 정보
        db.execute(text("""
            INSERT INTO package_purchases
            (customer_id, package_id, purchase_date, expiry_date, total_sessions, used_sessions, remaining_sessions, price_paid)
            VALUES (:customer_id, :package_id, :purchase_date, :expiry_date, :total_sessions, :used_sessions, :remaining_sessions, :price_paid)
        """), {
            'customer_id': customer.customer_id,
            'package_id': pulse_package.package_id,
            'purchase_date': date(2024, 1, 1),
            'expiry_date': date(2025, 12, 31),
            'total_sessions': 24,
            'used_sessions': 9,
            'remaining_sessions': 15,
            'price_paid': 960000
        })
        print("펄스 패키지 구매 정보 생성: 24회 중 9회 사용, 15회 잔여")

        # 림프 패키지
        lymph_package = db.query(Package).filter(Package.package_name.like('%림프%')).first()
        if not lymph_package:
            lymph_package = Package(
                package_name="림프 24회 패키지",
                total_sessions=24,
                base_price=960000,  # 40,000원 * 24회
                valid_months=12,
                is_active=True,
                description="하체 림프 관리 패키지"
            )
            db.add(lymph_package)
            db.commit()
            print("림프 패키지 생성")

        # 림프 패키지 구매 정보
        db.execute(text("""
            INSERT INTO package_purchases
            (customer_id, package_id, purchase_date, expiry_date, total_sessions, used_sessions, remaining_sessions, price_paid)
            VALUES (:customer_id, :package_id, :purchase_date, :expiry_date, :total_sessions, :used_sessions, :remaining_sessions, :price_paid)
        """), {
            'customer_id': customer.customer_id,
            'package_id': lymph_package.package_id,
            'purchase_date': date(2024, 1, 1),
            'expiry_date': date(2025, 12, 31),
            'total_sessions': 24,
            'used_sessions': 10,
            'remaining_sessions': 14,
            'price_paid': 960000
        })
        print("림프 패키지 구매 정보 생성: 24회 중 10회 사용, 14회 잔여")

        db.commit()

        # 서비스 타입 업데이트
        # 서비스 이용 기록의 서비스 타입을 정확히 분류
        service_usage_list = db.execute(text("""
            SELECT usage_id, session_details
            FROM service_usage
            WHERE customer_id = :customer_id
        """), {'customer_id': customer.customer_id}).fetchall()

        print(f"\n서비스 이용 기록 {len(service_usage_list)}건의 서비스 타입 업데이트 중...")

        for usage_id, details in service_usage_list:
            if details:
                details_lower = details.lower()
                service_type_id = 1  # 기본값: 상담

                if '하체' in details_lower or 'w/' in details_lower:
                    service_type_id = 3  # 림프
                elif '전신' in details_lower and ('링' in details_lower or '패드' in details_lower):
                    service_type_id = 2  # 펄스
                elif 'h(' in details_lower or '브레인' in details_lower:
                    service_type_id = 1  # 브레인
                elif '주' in details_lower and '1000' in details_lower:
                    service_type_id = 4  # 레드

                db.execute(text("""
                    UPDATE service_usage
                    SET service_type_id = :service_type_id
                    WHERE usage_id = :usage_id
                """), {'service_type_id': service_type_id, 'usage_id': usage_id})

        db.commit()
        print("서비스 타입 업데이트 완료")

        # 결과 확인
        result = db.execute(text("""
            SELECT p.package_name, pp.total_sessions, pp.used_sessions, pp.remaining_sessions
            FROM package_purchases pp
            JOIN packages p ON pp.package_id = p.package_id
            WHERE pp.customer_id = :customer_id
        """), {'customer_id': customer.customer_id}).fetchall()

        print("\n최종 패키지 정보:")
        for package_name, total, used, remaining in result:
            print(f"  - {package_name}: 전체 {total}회, 사용 {used}회, 잔여 {remaining}회")

if __name__ == "__main__":
    print("이성윤 고객 패키지 정보 정확히 마이그레이션 시작...")
    create_lee_packages()
    print("\n완료!")
