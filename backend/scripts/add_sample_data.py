import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.database import SessionLocal
from models.customer import Customer
from models.payment import Payment
from models.package import Package, PackagePurchase
from models.service import ServiceUsage
from datetime import date, timedelta
import random

def add_sample_data():
    db = SessionLocal()
    try:
        # 샘플 고객 추가
        customers = []
        customer_names = ['김영희', '이철수', '박민수', '최지연', '정대호']
        regions = ['서울 강서구', '서울 양천구', '서울 구로구', '서울 영등포구', '서울 마포구']
        sources = ['당근', '유튜브', '검색', '지인소개', '인스타그램']
        
        for i, name in enumerate(customer_names):
            customer = Customer(
                name=name,
                phone=f'010-{2000+i}-{3000+i}',
                first_visit_date=date.today() - timedelta(days=random.randint(1, 30)),
                region=regions[i % len(regions)],
                referral_source=sources[i % len(sources)],
                health_concerns='피로, 스트레스',
                assigned_staff='직원'
            )
            db.add(customer)
            customers.append(customer)
        
        db.flush()
        
        # 샘플 패키지 추가
        packages = []
        package_data = [
            ('브레인 10회', 10, 500000),
            ('펄스 10회', 10, 400000),
            ('림프 10회', 10, 450000),
            ('종합 20회', 20, 1500000),
            ('프리미엄 30회', 30, 2000000)
        ]
        
        for name, sessions, price in package_data:
            package = Package(
                package_name=name,
                total_sessions=sessions,
                price=price,
                valid_days=60,
                is_active=True
            )
            db.add(package)
            packages.append(package)
        
        db.flush()
        
        # 오늘 결제 추가
        for i in range(2):
            payment = Payment(
                customer_id=customers[i].customer_id,
                payment_date=date.today(),
                amount=random.choice([500000, 400000, 450000]),
                payment_method='card',
                payment_staff='직원',
                purchase_type='new',
                purchase_order=1
            )
            db.add(payment)
        
        # 이번달 결제 추가
        for i in range(15):
            payment = Payment(
                customer_id=random.choice(customers).customer_id,
                payment_date=date.today() - timedelta(days=random.randint(1, 25)),
                amount=random.choice([500000, 400000, 450000, 1500000]),
                payment_method=random.choice(['card', 'transfer', 'cash']),
                payment_staff='직원',
                purchase_type=random.choice(['new', 'renewal']),
                purchase_order=random.randint(1, 3)
            )
            db.add(payment)
        
        # 패키지 구매 추가
        for i, customer in enumerate(customers):
            purchase = PackagePurchase(
                customer_id=customer.customer_id,
                package_id=packages[i % len(packages)].package_id,
                purchase_date=date.today() - timedelta(days=random.randint(5, 30)),
                expiry_date=date.today() + timedelta(days=random.randint(30, 60)),
                total_sessions=packages[i % len(packages)].total_sessions,
                used_sessions=random.randint(0, 5),
                remaining_sessions=packages[i % len(packages)].total_sessions - random.randint(0, 5)
            )
            db.add(purchase)
        
        # 오늘 서비스 이용 추가
        for i in range(3):
            usage = ServiceUsage(
                customer_id=customers[i].customer_id,
                service_date=date.today(),
                service_type_id=random.randint(1, 4),
                package_id=packages[0].package_id,
                session_details='서비스 진행 완료',
                session_number=random.randint(1, 10),
                created_by='직원'
            )
            db.add(usage)
        
        db.commit()
        print('✅ 샘플 데이터 추가 완료!')
        print(f'- 고객: {len(customers)}명')
        print(f'- 패키지: {len(packages)}개')
        print(f'- 오늘 결제: 2건')
        print(f'- 이번달 결제: 15건')
        print(f'- 오늘 방문: 3명')
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()